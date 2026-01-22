/**
 * E2E Tests for Chatbot Feedback & Task List Display
 * Feature: 009-chatkit-frontend
 * Tasks: T051g, T051h, T051i
 *
 * Success Criteria:
 * - SC-013: 100% of task operations display confirmation message <2s
 * - SC-014: Task list queries return accurate data <2s
 * - SC-015: Dashboard refreshes <1s after chatbot confirmation
 */

import { test, expect, Page } from '@playwright/test';

// Test configuration
const TEST_USER_EMAIL = 'chatbot-feedback-test@example.com';
const TEST_USER_PASSWORD = 'TestPass123!';
const CONFIRMATION_TIMEOUT = 2000; // 2 seconds per SC-013, SC-014
const DASHBOARD_REFRESH_TIMEOUT = 1000; // 1 second per SC-015

/**
 * Helper: Sign in as test user
 */
async function signInAsTestUser(page: Page) {
  await page.goto('/auth/signin');

  await page.fill('input[type="email"]', TEST_USER_EMAIL);
  await page.fill('input[type="password"]', TEST_USER_PASSWORD);
  await page.click('button[type="submit"]');

  // Wait for redirect to dashboard
  await page.waitForURL('/dashboard', { timeout: 5000 });
}

/**
 * Helper: Open chatbot popup
 */
async function openChatbot(page: Page) {
  // Find and click floating action button (FAB)
  const fabButton = page.locator('[data-testid="chat-fab"], [aria-label*="chatbot" i], button:has-text("Chat")').first();
  await fabButton.click();

  // Wait for chatbot popup to appear
  await page.waitForSelector('[data-testid="chatbot-popup"], [role="dialog"]', { timeout: 3000 });
}

/**
 * Helper: Send message in chatbot
 */
async function sendChatMessage(page: Page, message: string) {
  // Find message input
  const messageInput = page.locator('[data-testid="chat-input"], textarea, input[placeholder*="task" i]').last();

  // Type message
  await messageInput.fill(message);

  // Submit message (Enter key or Send button)
  await messageInput.press('Enter');
}

/**
 * Helper: Wait for AI response to complete
 */
async function waitForAIResponse(page: Page, timeout = 10000) {
  // Wait for streaming indicator to disappear
  await page.waitForSelector('[data-testid="typing-indicator"], [aria-label*="typing" i]', {
    state: 'hidden',
    timeout,
  }).catch(() => {
    // Typing indicator might not appear for fast responses
    console.log('Typing indicator not found, continuing...');
  });

  // Wait a bit for final content to render
  await page.waitForTimeout(500);
}

test.describe('Chatbot Feedback & Task List Display', () => {
  test.beforeEach(async ({ page }) => {
    // Sign in before each test
    await signInAsTestUser(page);

    // Open chatbot
    await openChatbot(page);
  });

  // T051g: SC-013 - 100% of task operations display confirmation message within 2 seconds
  test('should display confirmation message for task creation within 2 seconds', async ({ page }) => {
    const startTime = Date.now();

    // Send task creation command
    await sendChatMessage(page, 'Add a task to test chatbot feedback');

    // Wait for AI response
    await waitForAIResponse(page);

    // Check for confirmation message (should contain checkmark and "added successfully" or similar)
    const confirmationMessage = page.locator('text=/✓|✅|created|added successfully/i').first();
    await expect(confirmationMessage).toBeVisible({ timeout: CONFIRMATION_TIMEOUT });

    const elapsedTime = Date.now() - startTime;

    // Verify timing constraint
    expect(elapsedTime).toBeLessThan(CONFIRMATION_TIMEOUT);

    console.log(`✓ Confirmation message displayed in ${elapsedTime}ms (SC-013: <2000ms)`);
  });

  test('should display confirmation message for task completion within 2 seconds', async ({ page }) => {
    // First, create a task to complete
    await sendChatMessage(page, 'Add a task to complete later');
    await waitForAIResponse(page);

    // Extract task ID from response (look for "ID: #XX" or "#XX")
    const responseText = await page.locator('[role="log"], [data-testid="message-list"]').last().textContent();
    const taskIdMatch = responseText?.match(/#(\d+)/);

    if (!taskIdMatch) {
      throw new Error('Could not extract task ID from chatbot response');
    }

    const taskId = taskIdMatch[1];
    const startTime = Date.now();

    // Send completion command
    await sendChatMessage(page, `Mark task ${taskId} as done`);

    // Wait for AI response
    await waitForAIResponse(page);

    // Check for confirmation message
    const confirmationMessage = page.locator(`text=/✓|✅|Task #${taskId}.*complete/i`).first();
    await expect(confirmationMessage).toBeVisible({ timeout: CONFIRMATION_TIMEOUT });

    const elapsedTime = Date.now() - startTime;
    expect(elapsedTime).toBeLessThan(CONFIRMATION_TIMEOUT);

    console.log(`✓ Completion confirmation displayed in ${elapsedTime}ms (SC-013: <2000ms)`);
  });

  test('should display confirmation message for task deletion within 2 seconds', async ({ page }) => {
    // First, create a task to delete
    await sendChatMessage(page, 'Add a task to delete later');
    await waitForAIResponse(page);

    // Extract task ID
    const responseText = await page.locator('[role="log"], [data-testid="message-list"]').last().textContent();
    const taskIdMatch = responseText?.match(/#(\d+)/);

    if (!taskIdMatch) {
      throw new Error('Could not extract task ID from chatbot response');
    }

    const taskId = taskIdMatch[1];
    const startTime = Date.now();

    // Send deletion command
    await sendChatMessage(page, `Delete task ${taskId}`);

    // Wait for AI response
    await waitForAIResponse(page);

    // Check for confirmation message
    const confirmationMessage = page.locator(`text=/✓|✅|Task #${taskId}.*deleted/i`).first();
    await expect(confirmationMessage).toBeVisible({ timeout: CONFIRMATION_TIMEOUT });

    const elapsedTime = Date.now() - startTime;
    expect(elapsedTime).toBeLessThan(CONFIRMATION_TIMEOUT);

    console.log(`✓ Deletion confirmation displayed in ${elapsedTime}ms (SC-013: <2000ms)`);
  });

  // T051h: SC-014 - Task list queries return accurate data within 2 seconds
  test('should display formatted task list when queried within 2 seconds', async ({ page }) => {
    // Create a few test tasks first
    await sendChatMessage(page, 'Add task: Buy groceries');
    await waitForAIResponse(page);

    await sendChatMessage(page, 'Add task: Call dentist');
    await waitForAIResponse(page);

    const startTime = Date.now();

    // Query for task list
    await sendChatMessage(page, 'Show my pending tasks');

    // Wait for AI response
    await waitForAIResponse(page);

    // Check for formatted task list (should contain task count, IDs, titles)
    const taskListResponse = page.locator('text=/You have.*task|pending task|\\[ID:/i').first();
    await expect(taskListResponse).toBeVisible({ timeout: CONFIRMATION_TIMEOUT });

    // Verify list contains task IDs and titles
    const responseText = await page.locator('[role="log"], [data-testid="message-list"]').last().textContent();
    expect(responseText).toMatch(/ID:?\s*\d+|#\d+/i); // Contains task IDs
    expect(responseText).toMatch(/Buy groceries|Call dentist/i); // Contains task titles

    const elapsedTime = Date.now() - startTime;
    expect(elapsedTime).toBeLessThan(CONFIRMATION_TIMEOUT);

    console.log(`✓ Task list displayed in ${elapsedTime}ms (SC-014: <2000ms)`);
  });

  test('should handle empty task list query gracefully', async ({ page }) => {
    // Assuming this is a fresh test user with no tasks, or we delete all tasks first
    const startTime = Date.now();

    // Query for tasks
    await sendChatMessage(page, 'List all my tasks');

    // Wait for AI response
    await waitForAIResponse(page);

    // Check for "no tasks" message
    const emptyMessage = page.locator('text=/no tasks|You have 0|don\'t have any/i').first();
    await expect(emptyMessage).toBeVisible({ timeout: CONFIRMATION_TIMEOUT });

    const elapsedTime = Date.now() - startTime;
    expect(elapsedTime).toBeLessThan(CONFIRMATION_TIMEOUT);

    console.log(`✓ Empty task list message displayed in ${elapsedTime}ms (SC-014: <2000ms)`);
  });

  // T051i: SC-015 - Dashboard refreshes within 1 second of chatbot confirmation
  test('should refresh dashboard within 1 second after task creation confirmation', async ({ page }) => {
    // Get initial task count from dashboard (in background)
    const initialTaskCount = await page.locator('[data-testid="task-card"], [role="article"]').count();

    // Create a task via chatbot
    await sendChatMessage(page, 'Add task: Dashboard refresh test');

    // Wait for confirmation message to appear
    const confirmationMessage = page.locator('text=/✓|✅|added successfully/i').first();
    await expect(confirmationMessage).toBeVisible({ timeout: CONFIRMATION_TIMEOUT });

    const confirmationTime = Date.now();

    // Close chatbot to see dashboard clearly
    const closeButton = page.locator('[aria-label*="close" i], button:has-text("×")').first();
    await closeButton.click().catch(() => {
      // If close button not found, press Escape
      page.keyboard.press('Escape');
    });

    // Wait for dashboard to show new task
    // Dashboard should have one more task than before
    await expect(async () => {
      const currentTaskCount = await page.locator('[data-testid="task-card"], [role="article"]').count();
      expect(currentTaskCount).toBe(initialTaskCount + 1);
    }).toPass({ timeout: DASHBOARD_REFRESH_TIMEOUT });

    const dashboardUpdateTime = Date.now() - confirmationTime;

    // Verify timing constraint
    expect(dashboardUpdateTime).toBeLessThan(DASHBOARD_REFRESH_TIMEOUT);

    console.log(`✓ Dashboard refreshed in ${dashboardUpdateTime}ms (SC-015: <1000ms)`);
  });

  test('should refresh dashboard within 1 second after task deletion confirmation', async ({ page }) => {
    // First create a task
    await sendChatMessage(page, 'Add task: To be deleted');
    await waitForAIResponse(page);

    // Extract task ID
    const responseText = await page.locator('[role="log"], [data-testid="message-list"]').last().textContent();
    const taskIdMatch = responseText?.match(/#(\d+)/);

    if (!taskIdMatch) {
      throw new Error('Could not extract task ID from chatbot response');
    }

    const taskId = taskIdMatch[1];

    // Get initial task count
    const initialTaskCount = await page.locator('[data-testid="task-card"], [role="article"]').count();

    // Delete the task
    await sendChatMessage(page, `Delete task ${taskId}`);

    // Wait for confirmation
    const confirmationMessage = page.locator(`text=/✓|✅|Task #${taskId}.*deleted/i`).first();
    await expect(confirmationMessage).toBeVisible({ timeout: CONFIRMATION_TIMEOUT });

    const confirmationTime = Date.now();

    // Close chatbot
    const closeButton = page.locator('[aria-label*="close" i], button:has-text("×")').first();
    await closeButton.click().catch(() => {
      page.keyboard.press('Escape');
    });

    // Wait for dashboard to remove the task
    await expect(async () => {
      const currentTaskCount = await page.locator('[data-testid="task-card"], [role="article"]').count();
      expect(currentTaskCount).toBe(initialTaskCount - 1);
    }).toPass({ timeout: DASHBOARD_REFRESH_TIMEOUT });

    const dashboardUpdateTime = Date.now() - confirmationTime;
    expect(dashboardUpdateTime).toBeLessThan(DASHBOARD_REFRESH_TIMEOUT);

    console.log(`✓ Dashboard refreshed after deletion in ${dashboardUpdateTime}ms (SC-015: <1000ms)`);
  });
});
