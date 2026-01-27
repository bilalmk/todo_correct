/**
 * Comprehensive Application Test Script
 * Tests the complete flow of the Todo application
 */

const FRONTEND_URL = "http://localhost:3000";
const BACKEND_URL = "http://localhost:8000";
const TEST_EMAIL = "bilalmk@gmail.com";
const TEST_PASSWORD = "bilal12345"; // User's actual password

let cookies = "";
let jwtToken = "";
let userUuid = "";

// Helper to extract cookies from response
function extractCookies(response) {
  const setCookie = response.headers.raw()["set-cookie"];
  if (setCookie) {
    return setCookie.map(cookie => cookie.split(';')[0]).join('; ');
  }
  return "";
}

// Helper to make authenticated requests
async function fetchWithCookies(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      "Cookie": cookies,
    },
  });

  // Update cookies
  const newCookies = extractCookies(response);
  if (newCookies) {
    cookies = newCookies;
  }

  return response;
}

// Test 1: Login
async function testLogin() {
  console.log("\n=== Test 1: Login ===");

  try {
    const response = await fetch(`${FRONTEND_URL}/api/auth/sign-in/email`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: TEST_EMAIL,
        password: TEST_PASSWORD,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Login failed: ${response.status} - ${error}`);
    }

    // Extract cookies from login response
    cookies = extractCookies(response);
    console.log("✓ Login successful");
    console.log(`✓ Cookies: ${cookies.substring(0, 50)}...`);

    return true;
  } catch (error) {
    console.error("✗ Login failed:", error.message);
    return false;
  }
}

// Test 2: Get Session
async function testGetSession() {
  console.log("\n=== Test 2: Get Session ===");

  try {
    const response = await fetchWithCookies(`${FRONTEND_URL}/api/auth/get-session`);

    if (!response.ok) {
      throw new Error(`Get session failed: ${response.status}`);
    }

    const session = await response.json();
    console.log("✓ Session retrieved");
    console.log(`✓ User: ${session.user?.email}`);
    console.log(`✓ User ID: ${session.user?.id}`);

    return true;
  } catch (error) {
    console.error("✗ Get session failed:", error.message);
    return false;
  }
}

// Test 3: Get JWT Token
async function testGetJwtToken() {
  console.log("\n=== Test 3: Get JWT Token ===");

  try {
    const response = await fetchWithCookies(`${FRONTEND_URL}/api/auth/get-token`);

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Get token failed: ${response.status} - ${error}`);
    }

    const data = await response.json();
    jwtToken = data.token;

    console.log("✓ JWT token retrieved");
    console.log(`✓ Token: ${jwtToken.substring(0, 50)}...`);

    // Decode JWT to get UUID
    const payload = JSON.parse(Buffer.from(jwtToken.split('.')[1], 'base64').toString());
    userUuid = payload.uuid;
    console.log(`✓ User UUID: ${userUuid}`);

    return true;
  } catch (error) {
    console.error("✗ Get JWT token failed:", error.message);
    return false;
  }
}

// Test 4: Create Tag
async function testCreateTag() {
  console.log("\n=== Test 4: Create Tag ===");

  try {
    const tagData = {
      name: `Test Tag ${Date.now()}`,
      color: "#3B82F6",
    };

    const response = await fetch(`${BACKEND_URL}/api/v1/${userUuid}/tags`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${jwtToken}`,
      },
      body: JSON.stringify(tagData),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Create tag failed: ${response.status} - ${error}`);
    }

    const tag = await response.json();
    console.log("✓ Tag created successfully");
    console.log(`✓ Tag ID: ${tag.id}`);
    console.log(`✓ Tag Name: ${tag.name}`);

    return tag.id;
  } catch (error) {
    console.error("✗ Create tag failed:", error.message);
    return null;
  }
}

// Test 5: Get Tags
async function testGetTags() {
  console.log("\n=== Test 5: Get Tags ===");

  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/${userUuid}/tags`, {
      headers: {
        "Authorization": `Bearer ${jwtToken}`,
      },
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Get tags failed: ${response.status} - ${error}`);
    }

    const tags = await response.json();
    console.log("✓ Tags retrieved successfully");
    console.log(`✓ Total tags: ${tags.length}`);

    return true;
  } catch (error) {
    console.error("✗ Get tags failed:", error.message);
    return false;
  }
}

// Test 6: Create Task
async function testCreateTask(tagId) {
  console.log("\n=== Test 6: Create Task ===");

  try {
    const taskData = {
      title: `Test Task ${Date.now()}`,
      description: "This is a test task",
      priority: "high",
      completed: false,
      tags: tagId ? [tagId] : [],
    };

    const response = await fetch(`${BACKEND_URL}/api/v1/${userUuid}/tasks`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${jwtToken}`,
      },
      body: JSON.stringify(taskData),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Create task failed: ${response.status} - ${error}`);
    }

    const task = await response.json();
    console.log("✓ Task created successfully");
    console.log(`✓ Task ID: ${task.id}`);
    console.log(`✓ Task Title: ${task.title}`);

    return task.id;
  } catch (error) {
    console.error("✗ Create task failed:", error.message);
    return null;
  }
}

// Test 7: Get Tasks
async function testGetTasks() {
  console.log("\n=== Test 7: Get Tasks ===");

  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/${userUuid}/tasks`, {
      headers: {
        "Authorization": `Bearer ${jwtToken}`,
      },
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Get tasks failed: ${response.status} - ${error}`);
    }

    const data = await response.json();
    console.log("✓ Tasks retrieved successfully");
    console.log(`✓ Total tasks: ${data.total}`);
    console.log(`✓ Items in current page: ${data.items.length}`);

    return true;
  } catch (error) {
    console.error("✗ Get tasks failed:", error.message);
    return false;
  }
}

// Test 8: Filter Tasks
async function testFilterTasks() {
  console.log("\n=== Test 8: Filter Tasks ===");

  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/${userUuid}/tasks?priority=high&status=incomplete`, {
      headers: {
        "Authorization": `Bearer ${jwtToken}`,
      },
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Filter tasks failed: ${response.status} - ${error}`);
    }

    const data = await response.json();
    console.log("✓ Tasks filtered successfully");
    console.log(`✓ High priority incomplete tasks: ${data.items.length}`);

    return true;
  } catch (error) {
    console.error("✗ Filter tasks failed:", error.message);
    return false;
  }
}

// Run all tests
async function runTests() {
  console.log("====================================");
  console.log("  Todo Application Test Suite");
  console.log("====================================");

  const results = {
    passed: 0,
    failed: 0,
  };

  // Test sequence
  if (await testLogin()) {
    results.passed++;
  } else {
    results.failed++;
    console.log("\n✗ Cannot proceed without login");
    return results;
  }

  if (await testGetSession()) {
    results.passed++;
  } else {
    results.failed++;
  }

  if (await testGetJwtToken()) {
    results.passed++;
  } else {
    results.failed++;
    console.log("\n✗ Cannot proceed without JWT token");
    return results;
  }

  const tagId = await testCreateTag();
  if (tagId) {
    results.passed++;
  } else {
    results.failed++;
  }

  if (await testGetTags()) {
    results.passed++;
  } else {
    results.failed++;
  }

  const taskId = await testCreateTask(tagId);
  if (taskId) {
    results.passed++;
  } else {
    results.failed++;
  }

  if (await testGetTasks()) {
    results.passed++;
  } else {
    results.failed++;
  }

  if (await testFilterTasks()) {
    results.passed++;
  } else {
    results.failed++;
  }

  // Summary
  console.log("\n====================================");
  console.log("  Test Summary");
  console.log("====================================");
  console.log(`✓ Passed: ${results.passed}`);
  console.log(`✗ Failed: ${results.failed}`);
  console.log(`Total: ${results.passed + results.failed}`);

  if (results.failed === 0) {
    console.log("\n🎉 All tests passed!");
  } else {
    console.log("\n⚠️  Some tests failed. Please review the errors above.");
  }

  return results;
}

// Run the tests
runTests().then(results => {
  process.exit(results.failed > 0 ? 1 : 0);
}).catch(error => {
  console.error("\n✗ Test suite crashed:", error);
  process.exit(1);
});
