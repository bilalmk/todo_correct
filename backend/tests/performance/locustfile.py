"""
Load Testing with Locust (T050)
Test 100 concurrent users with p95 latency <100ms per SC-008

Success Criteria:
- SC-008: Supports 100 concurrent users with p95 latency <100ms
- JWKS cache remains performant under load
- No auth failures under concurrent load

Built following skills:
- @.claude/skills/panaversity/betterauth-fastapi-jwt-bridge (load testing patterns)

Usage:
    # Start backend server first
    cd backend
    uvicorn src.main:app --reload

    # Run load test (100 concurrent users)
    locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
           --users 100 --spawn-rate 10 --run-time 2m --headless

    # With web UI for real-time monitoring
    locust -f tests/performance/locustfile.py --host=http://localhost:8000

    Then visit http://localhost:8089
"""

from locust import HttpUser, task, between, events
import random
import json
import time
from datetime import datetime

# Test user credentials (pre-registered users for load testing)
# In production, you would pre-populate these users in the database
TEST_USERS = [
    {"email": f"loadtest{i}@example.com", "password": "LoadTest123!"}
    for i in range(100)
]


class TodoAppUser(HttpUser):
    """
    Simulates a typical todo app user behavior:
    1. Register (if new) or Login
    2. Create tasks
    3. List tasks (with/without filters)
    4. Update tasks (mark complete)
    5. Delete tasks
    """

    wait_time = between(1, 3)  # Realistic user think time (1-3 seconds)

    def on_start(self):
        """
        Called when a simulated user starts.
        Register or login to get JWT token.
        """
        # Use a random test user
        self.user_data = random.choice(TEST_USERS)
        self.jwt_token = None
        self.user_id = None
        self.created_task_ids = []

        # Try to login (assumes users are pre-registered)
        # If login fails, register first
        self.login()

    def login(self):
        """Login and store JWT token"""
        response = self.client.post(
            "/api/auth/sign-in/email",
            json={
                "email": self.user_data["email"],
                "password": self.user_data["password"],
            },
            name="/api/auth/sign-in/email (Login)",
        )

        if response.status_code == 200:
            data = response.json()
            self.jwt_token = data.get("token")
            self.user_id = data.get("user", {}).get("id")
        elif response.status_code in [401, 404]:
            # User doesn't exist, register first
            self.register()
        else:
            print(f"Login failed: {response.status_code} - {response.text}")

    def register(self):
        """Register new user if login fails"""
        response = self.client.post(
            "/api/auth/sign-up",
            json={
                "name": f"Load Test User {self.user_data['email']}",
                "email": self.user_data["email"],
                "password": self.user_data["password"],
            },
            name="/api/auth/sign-up (Register)",
        )

        if response.status_code == 201:
            data = response.json()
            self.jwt_token = data.get("token")
            self.user_id = data.get("user", {}).get("id")
        else:
            print(f"Registration failed: {response.status_code} - {response.text}")

    def get_headers(self):
        """Get authorization headers with JWT token"""
        if not self.jwt_token:
            return {}
        return {"Authorization": f"Bearer {self.jwt_token}"}

    @task(5)
    def list_tasks(self):
        """
        List all tasks (most common operation)
        Weight: 5 (50% of operations)
        """
        if not self.user_id:
            return

        with self.client.get(
            f"/api/v1/{self.user_id}/tasks",
            headers=self.get_headers(),
            catch_response=True,
            name="/api/v1/{user_id}/tasks (List)",
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                response.failure("Authentication failed - JWT expired or invalid")
            else:
                response.failure(f"Unexpected status: {response.status_code}")

    @task(3)
    def create_task(self):
        """
        Create a new task
        Weight: 3 (30% of operations)
        """
        if not self.user_id:
            return

        task_data = {
            "title": f"Load Test Task {random.randint(1000, 9999)}",
            "description": f"Created at {datetime.now().isoformat()}",
            "completed": False,
            "priority": random.choice(["high", "medium", "low"]),
        }

        with self.client.post(
            f"/api/v1/{self.user_id}/tasks",
            json=task_data,
            headers=self.get_headers(),
            catch_response=True,
            name="/api/v1/{user_id}/tasks (Create)",
        ) as response:
            if response.status_code == 201:
                data = response.json()
                self.created_task_ids.append(data.get("id"))
                response.success()
            else:
                response.failure(f"Create failed: {response.status_code}")

    @task(2)
    def update_task(self):
        """
        Update a task (mark as complete)
        Weight: 2 (20% of operations)
        """
        if not self.user_id or not self.created_task_ids:
            return

        task_id = random.choice(self.created_task_ids)

        with self.client.patch(
            f"/api/v1/{self.user_id}/tasks/{task_id}",
            json={"completed": True},
            headers=self.get_headers(),
            catch_response=True,
            name="/api/v1/{user_id}/tasks/{task_id} (Update)",
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                # Task might have been deleted
                self.created_task_ids.remove(task_id)
                response.success()
            else:
                response.failure(f"Update failed: {response.status_code}")

    @task(1)
    def list_tasks_with_filter(self):
        """
        List tasks with filters (priority, status, search)
        Weight: 1 (10% of operations)
        """
        if not self.user_id:
            return

        # Random filter combinations
        filters = {
            "priority": random.choice(["high", "medium", "low", None]),
            "completed": random.choice([True, False, None]),
            "search": random.choice(["Load Test", None]),
        }

        # Build query params (excluding None values)
        params = {k: v for k, v in filters.items() if v is not None}

        with self.client.get(
            f"/api/v1/{self.user_id}/tasks",
            params=params,
            headers=self.get_headers(),
            catch_response=True,
            name="/api/v1/{user_id}/tasks?filters (List Filtered)",
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Filter failed: {response.status_code}")

    @task(1)
    def delete_task(self):
        """
        Delete a task
        Weight: 1 (10% of operations)
        """
        if not self.user_id or not self.created_task_ids:
            return

        task_id = random.choice(self.created_task_ids)

        with self.client.delete(
            f"/api/v1/{self.user_id}/tasks/{task_id}",
            headers=self.get_headers(),
            catch_response=True,
            name="/api/v1/{user_id}/tasks/{task_id} (Delete)",
        ) as response:
            if response.status_code in [200, 204]:
                self.created_task_ids.remove(task_id)
                response.success()
            elif response.status_code == 404:
                # Already deleted
                self.created_task_ids.remove(task_id)
                response.success()
            else:
                response.failure(f"Delete failed: {response.status_code}")


# Custom metrics for SC-008 validation
latencies = []


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Collect response times for p95 calculation"""
    if exception is None:
        latencies.append(response_time)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    Calculate and report p95 latency after test completes
    Validates SC-008: p95 latency <100ms
    """
    if not latencies:
        print("\n[ERROR] No latencies recorded - test may have failed")
        return

    sorted_latencies = sorted(latencies)
    p95_index = int(len(sorted_latencies) * 0.95)
    p95_latency = sorted_latencies[p95_index] if p95_index < len(sorted_latencies) else 0

    p50_index = int(len(sorted_latencies) * 0.50)
    p50_latency = sorted_latencies[p50_index]

    p99_index = int(len(sorted_latencies) * 0.99)
    p99_latency = sorted_latencies[p99_index] if p99_index < len(sorted_latencies) else 0

    min_latency = sorted_latencies[0]
    max_latency = sorted_latencies[-1]
    avg_latency = sum(latencies) / len(latencies)

    print("\n" + "=" * 60)
    print("PERFORMANCE SUMMARY (SC-008 Validation)")
    print("=" * 60)
    print(f"Total Requests: {len(latencies)}")
    print(f"Min Latency: {min_latency:.2f}ms")
    print(f"Avg Latency: {avg_latency:.2f}ms")
    print(f"P50 Latency: {p50_latency:.2f}ms")
    print(f"P95 Latency: {p95_latency:.2f}ms")
    print(f"P99 Latency: {p99_latency:.2f}ms")
    print(f"Max Latency: {max_latency:.2f}ms")
    print("-" * 60)

    # SC-008 validation
    if p95_latency < 100:
        print(f"✅ SC-008 PASS: P95 latency {p95_latency:.2f}ms < 100ms")
    else:
        print(f"❌ SC-008 FAIL: P95 latency {p95_latency:.2f}ms >= 100ms")

    print("=" * 60 + "\n")


# Custom scenario for quick SC-008 validation
# Run: locust -f locustfile.py --host=http://localhost:8000 \
#            --users 100 --spawn-rate 10 --run-time 2m --headless
