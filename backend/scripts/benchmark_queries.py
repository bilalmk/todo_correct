"""Performance benchmark script using EXPLAIN ANALYZE.

Verifies sub-100ms performance targets for critical queries.

Usage:
    python scripts/benchmark_queries.py
"""
import asyncio
import time
from typing import List, Tuple
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.models.user import User
from src.models.task import Task
from src.models.tag import Tag
from sqlmodel import select


class QueryBenchmark:
    """Benchmark database queries and verify performance targets."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.results: List[Tuple[str, float, bool, str]] = []

    async def run_query_with_timing(
        self, name: str, query: str, params: dict, target_ms: float = 100.0
    ) -> Tuple[str, float, bool, str]:
        """Run a query, measure execution time, and get EXPLAIN ANALYZE output."""
        # Get EXPLAIN ANALYZE output
        explain_query = f"EXPLAIN ANALYZE {query}"
        result = await self.session.execute(text(explain_query), params)
        explain_output = "\n".join([row[0] for row in result.fetchall()])

        # Extract actual execution time from EXPLAIN ANALYZE
        # Look for "Execution Time" in the output
        execution_time_ms = None
        for line in explain_output.split("\n"):
            if "Execution Time:" in line:
                # Extract the number before "ms"
                time_str = line.split("Execution Time:")[1].strip().split(" ms")[0]
                execution_time_ms = float(time_str)
                break

        if execution_time_ms is None:
            # Fallback: measure time manually
            start_time = time.perf_counter()
            await self.session.execute(text(query), params)
            end_time = time.perf_counter()
            execution_time_ms = (end_time - start_time) * 1000

        passed = execution_time_ms < target_ms

        return (name, execution_time_ms, passed, explain_output)

    async def benchmark_task_queries(self, user_id: UUID) -> None:
        """Benchmark task-related queries."""
        print("\n📊 Benchmarking Task Queries...")
        print("=" * 80)

        # 1. Query for incomplete tasks (uses idx_tasks_user_completed)
        result = await self.run_query_with_timing(
            name="Get incomplete tasks",
            query="""
                SELECT * FROM tasks
                WHERE user_id = :user_id AND completed = FALSE
            """,
            params={"user_id": str(user_id)},
            target_ms=50.0,
        )
        self.results.append(result)

        # 2. Query for high priority tasks (uses idx_tasks_user_priority)
        result = await self.run_query_with_timing(
            name="Get high priority tasks",
            query="""
                SELECT * FROM tasks
                WHERE user_id = :user_id AND priority = 'high'
            """,
            params={"user_id": str(user_id)},
            target_ms=50.0,
        )
        self.results.append(result)

        # 3. Query for tasks due in next 7 days (uses idx_tasks_user_due_date)
        result = await self.run_query_with_timing(
            name="Get tasks due soon",
            query="""
                SELECT * FROM tasks
                WHERE user_id = :user_id
                  AND due_date IS NOT NULL
                  AND due_date >= NOW()
                  AND due_date <= NOW() + INTERVAL '7 days'
            """,
            params={"user_id": str(user_id)},
            target_ms=50.0,
        )
        self.results.append(result)

        # 4. Query for upcoming reminders (uses idx_tasks_due_reminders)
        result = await self.run_query_with_timing(
            name="Get upcoming reminders",
            query="""
                SELECT * FROM tasks
                WHERE completed = FALSE
                  AND deleted_at IS NULL
                  AND due_date IS NOT NULL
                  AND reminder_at IS NOT NULL
                  AND due_date >= NOW()
                  AND due_date <= NOW() + INTERVAL '7 days'
            """,
            params={},
            target_ms=50.0,
        )
        self.results.append(result)

    async def benchmark_search_queries(self, user_id: UUID) -> None:
        """Benchmark full-text search queries."""
        print("\n🔍 Benchmarking Full-Text Search Queries...")
        print("=" * 80)

        # 1. Basic full-text search (uses idx_tasks_fulltext_search GIN index)
        result = await self.run_query_with_timing(
            name="Full-text search (basic)",
            query="""
                SELECT id, title, description,
                       ts_rank(
                           to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')),
                           plainto_tsquery('english', :search_term)
                       ) AS rank
                FROM tasks
                WHERE user_id = :user_id
                  AND to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
                      @@ plainto_tsquery('english', :search_term)
                ORDER BY rank DESC
                LIMIT 100
            """,
            params={"user_id": str(user_id), "search_term": "meeting project"},
            target_ms=100.0,
        )
        self.results.append(result)

        # 2. Prefix search (uses idx_tasks_fulltext_search)
        result = await self.run_query_with_timing(
            name="Full-text search (prefix)",
            query="""
                SELECT id, title
                FROM tasks
                WHERE user_id = :user_id
                  AND to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
                      @@ to_tsquery('english', :search_term)
            """,
            params={"user_id": str(user_id), "search_term": "data:*"},
            target_ms=100.0,
        )
        self.results.append(result)

    async def benchmark_tag_queries(self, user_id: UUID) -> None:
        """Benchmark tag-related queries."""
        print("\n🏷️  Benchmarking Tag Queries...")
        print("=" * 80)

        # 1. Get user's tags (uses idx_tags_user_id)
        result = await self.run_query_with_timing(
            name="Get user tags",
            query="""
                SELECT * FROM tags
                WHERE user_id = :user_id AND deleted_at IS NULL
            """,
            params={"user_id": str(user_id)},
            target_ms=50.0,
        )
        self.results.append(result)

        # 2. Check unique tag name (uses idx_tags_user_name_unique)
        result = await self.run_query_with_timing(
            name="Check tag uniqueness",
            query="""
                SELECT COUNT(*) FROM tags
                WHERE user_id = :user_id
                  AND name = :tag_name
                  AND deleted_at IS NULL
            """,
            params={"user_id": str(user_id), "tag_name": "Work"},
            target_ms=50.0,
        )
        self.results.append(result)

    async def benchmark_notification_queries(self, user_id: UUID) -> None:
        """Benchmark notification-related queries."""
        print("\n🔔 Benchmarking Notification Queries...")
        print("=" * 80)

        # 1. Get pending notifications (uses idx_notifications_pending)
        result = await self.run_query_with_timing(
            name="Get pending notifications",
            query="""
                SELECT * FROM notifications
                WHERE user_id = :user_id AND status = 'pending'
            """,
            params={"user_id": str(user_id)},
            target_ms=50.0,
        )
        self.results.append(result)

        # 2. Get task notifications (uses idx_notifications_task_id)
        result = await self.run_query_with_timing(
            name="Get task notifications",
            query="""
                SELECT * FROM notifications
                WHERE task_id IS NOT NULL
                LIMIT 100
            """,
            params={},
            target_ms=50.0,
        )
        self.results.append(result)

    def print_results(self) -> None:
        """Print benchmark results in a formatted table."""
        print("\n" + "=" * 80)
        print("📈 BENCHMARK RESULTS")
        print("=" * 80)

        # Print summary table
        print(f"\n{'Query Name':<35} {'Time (ms)':<12} {'Target (ms)':<12} {'Status':<10}")
        print("-" * 80)

        passed_count = 0
        failed_count = 0

        for name, time_ms, passed, _ in self.results:
            status = "✅ PASS" if passed else "❌ FAIL"
            target = "< 100ms" if "search" in name.lower() else "< 50ms"

            print(f"{name:<35} {time_ms:>10.2f}   {target:<12} {status:<10}")

            if passed:
                passed_count += 1
            else:
                failed_count += 1

        # Print summary
        print("\n" + "=" * 80)
        print(f"Total Queries: {len(self.results)}")
        print(f"Passed: {passed_count} ✅")
        print(f"Failed: {failed_count} ❌")
        print("=" * 80)

        # Print detailed EXPLAIN output for failed queries
        if failed_count > 0:
            print("\n" + "=" * 80)
            print("🔍 EXPLAIN ANALYZE OUTPUT FOR FAILED QUERIES")
            print("=" * 80)

            for name, time_ms, passed, explain_output in self.results:
                if not passed:
                    print(f"\n❌ {name} ({time_ms:.2f}ms)")
                    print("-" * 80)
                    print(explain_output)
                    print()

    async def run_all_benchmarks(self) -> bool:
        """Run all benchmarks and return True if all passed."""
        # Get a test user
        result = await self.session.execute(select(User))
        user = result.scalars().first()

        if not user:
            print("❌ No users found in database. Please run seed_database.py first.")
            return False

        print(f"\n🎯 Running benchmarks for user: {user.name} ({user.email})")

        # Run all benchmark categories
        await self.benchmark_task_queries(user.id)
        await self.benchmark_search_queries(user.id)
        await self.benchmark_tag_queries(user.id)
        await self.benchmark_notification_queries(user.id)

        # Print results
        self.print_results()

        # Return True if all queries passed
        return all(passed for _, _, passed, _ in self.results)


async def main() -> None:
    """Main entry point for benchmark script."""
    print("🚀 Starting Performance Benchmarks...")
    print("=" * 80)

    async for session in get_session():
        try:
            benchmark = QueryBenchmark(session)
            all_passed = await benchmark.run_all_benchmarks()

            if all_passed:
                print("\n✅ All performance targets met!")
                exit(0)
            else:
                print("\n❌ Some queries did not meet performance targets.")
                print("   Consider adding or optimizing indexes.")
                exit(1)

        except Exception as e:
            print(f"\n❌ Error during benchmarking: {e}")
            raise
        finally:
            await session.close()
            break


if __name__ == "__main__":
    asyncio.run(main())
