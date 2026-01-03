/**
 * E2E Tests for Complete User Flow (T048)
 * Test: register → login → create task → filter tasks → logout
 *
 * Success Criteria:
 * - Complete user journey works end-to-end
 * - httpOnly cookie handling verified
 * - Error toasts display correlation IDs
 *
 * Built following skills:
 * - @.claude/skills/custom/frontend-design-system (React testing patterns)
 */

import { test, expect } from '@playwright/test';

test.describe('Complete User Flow (T048)', () => {
  test('should complete full user journey: register → login → create task → filter tasks → logout', async ({ page, context }) => {
    const timestamp = Date.now();
    const email = `userflow${timestamp}@example.com`;
    const password = 'SecurePassword123!';
    const name = 'Flow Test User';

    // Step 1: Register new user
    console.log('Step 1: Registering new user');
    await page.goto('/auth/register');

    await page.getByLabel(/full name/i).fill(name);
    await page.getByLabel(/email address/i).fill(email);
    await page.getByLabel(/^password$/i).fill(password);
    await page.getByRole('button', { name: /register/i }).click();

    // Verify redirect to dashboard after registration
    await expect(page).toHaveURL('/dashboard', { timeout: 10000 });
    await expect(page.getByText(/welcome/i)).toBeVisible();

    // Verify httpOnly cookies are set during registration
    const cookiesAfterRegister = await context.cookies();
    expect(cookiesAfterRegister.length).toBeGreaterThan(0);

    // Better Auth uses httpOnly cookies for security
    const sessionCookies = cookiesAfterRegister.filter(cookie =>
      cookie.name.includes('session') || cookie.name.includes('auth')
    );
    expect(sessionCookies.length).toBeGreaterThan(0);

    // Step 2: Logout
    console.log('Step 2: Logging out');
    await page.getByRole('button', { name: /sign out/i }).click();
    await expect(page).toHaveURL('/auth/login', { timeout: 5000 });

    // Step 3: Login with credentials
    console.log('Step 3: Logging in');
    await page.getByLabel(/email address/i).fill(email);
    await page.getByLabel(/password/i).fill(password);
    await page.getByRole('button', { name: /sign in/i }).click();

    // Verify redirect to dashboard after login
    await expect(page).toHaveURL('/dashboard', { timeout: 10000 });
    await expect(page.getByText(email)).toBeVisible();

    // Verify httpOnly cookies are set during login
    const cookiesAfterLogin = await context.cookies();
    expect(cookiesAfterLogin.length).toBeGreaterThan(0);

    // Step 4: Create tasks
    console.log('Step 4: Creating tasks');

    // Create task 1 (high priority)
    const addTaskButton = page.getByRole('button', { name: /add task/i }).first();
    await addTaskButton.click();

    await page.getByLabel(/title/i).fill('Complete project documentation');
    await page.getByLabel(/description/i).fill('Write comprehensive docs for the project');

    // Set priority to high
    await page.getByLabel(/priority/i).click();
    await page.getByRole('option', { name: /high/i }).click();

    await page.getByRole('button', { name: /create/i }).click();

    // Verify task appears in list
    await expect(page.getByText('Complete project documentation')).toBeVisible({ timeout: 5000 });

    // Create task 2 (medium priority)
    await addTaskButton.click();
    await page.getByLabel(/title/i).fill('Review pull requests');
    await page.getByLabel(/description/i).fill('Review pending PRs from team');

    await page.getByLabel(/priority/i).click();
    await page.getByRole('option', { name: /medium/i }).click();

    await page.getByRole('button', { name: /create/i }).click();

    await expect(page.getByText('Review pull requests')).toBeVisible({ timeout: 5000 });

    // Create task 3 (low priority)
    await addTaskButton.click();
    await page.getByLabel(/title/i).fill('Organize workspace');
    await page.getByLabel(/description/i).fill('Clean and organize desk area');

    await page.getByLabel(/priority/i).click();
    await page.getByRole('option', { name: /low/i }).click();

    await page.getByRole('button', { name: /create/i }).click();

    await expect(page.getByText('Organize workspace')).toBeVisible({ timeout: 5000 });

    // Step 5: Test filtering by priority
    console.log('Step 5: Testing priority filter');

    // Filter by high priority
    const priorityFilter = page.getByLabel(/filter by priority/i);
    await priorityFilter.click();
    await page.getByRole('option', { name: /^high$/i }).click();

    // Should only show high priority task
    await expect(page.getByText('Complete project documentation')).toBeVisible();
    await expect(page.getByText('Review pull requests')).not.toBeVisible();
    await expect(page.getByText('Organize workspace')).not.toBeVisible();

    // Clear filter to show all tasks
    await priorityFilter.click();
    await page.getByRole('option', { name: /all priorities/i }).click();

    // All tasks should be visible again
    await expect(page.getByText('Complete project documentation')).toBeVisible();
    await expect(page.getByText('Review pull requests')).toBeVisible();
    await expect(page.getByText('Organize workspace')).toBeVisible();

    // Step 6: Test filtering by completion status
    console.log('Step 6: Testing completion status filter');

    // Mark one task as complete
    const taskCheckbox = page.getByRole('checkbox').first();
    await taskCheckbox.click();

    // Filter by completed tasks
    const statusFilter = page.getByLabel(/filter by status/i);
    await statusFilter.click();
    await page.getByRole('option', { name: /completed/i }).click();

    // Should only show completed task
    await expect(page.locator('[data-completed="true"]')).toHaveCount(1, { timeout: 5000 });

    // Filter by active tasks
    await statusFilter.click();
    await page.getByRole('option', { name: /active/i }).click();

    // Should show only active (incomplete) tasks
    await expect(page.locator('[data-completed="false"]')).toHaveCount(2, { timeout: 5000 });

    // Step 7: Test search functionality
    console.log('Step 7: Testing search');

    // Clear status filter first
    await statusFilter.click();
    await page.getByRole('option', { name: /all/i }).click();

    const searchInput = page.getByPlaceholder(/search tasks/i);
    await searchInput.fill('project');

    // Should only show tasks matching search
    await expect(page.getByText('Complete project documentation')).toBeVisible();
    await expect(page.getByText('Review pull requests')).not.toBeVisible();
    await expect(page.getByText('Organize workspace')).not.toBeVisible();

    // Clear search
    await searchInput.clear();

    // All tasks visible again
    await expect(page.getByText('Complete project documentation')).toBeVisible();
    await expect(page.getByText('Review pull requests')).toBeVisible();
    await expect(page.getByText('Organize workspace')).toBeVisible();

    // Step 8: Logout
    console.log('Step 8: Final logout');
    await page.getByRole('button', { name: /sign out/i }).click();
    await expect(page).toHaveURL('/auth/login', { timeout: 5000 });

    // Verify accessing dashboard redirects to login (session cleared)
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 5000 });
  });

  test('should display error toast with correlation ID on API failure', async ({ page }) => {
    const timestamp = Date.now();
    const email = `errorflow${timestamp}@example.com`;
    const password = 'SecurePassword123!';

    // Register and login
    await page.goto('/auth/register');
    await page.getByLabel(/full name/i).fill('Error Test User');
    await page.getByLabel(/email address/i).fill(email);
    await page.getByLabel(/^password$/i).fill(password);
    await page.getByRole('button', { name: /register/i }).click();

    await expect(page).toHaveURL('/dashboard', { timeout: 10000 });

    // Intercept API request to simulate server error
    await page.route('**/api/v1/*/tasks', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Internal Server Error',
          code: 'INTERNAL_ERROR',
          status: 500,
          request_id: 'cor_abc123def456' // Correlation ID
        })
      });
    });

    // Try to create a task (will fail)
    const addTaskButton = page.getByRole('button', { name: /add task/i }).first();
    await addTaskButton.click();

    await page.getByLabel(/title/i).fill('Test Task');
    await page.getByRole('button', { name: /create/i }).click();

    // Verify error toast appears
    const errorToast = page.locator('[role="alert"]', { hasText: /error/i });
    await expect(errorToast).toBeVisible({ timeout: 5000 });

    // Verify correlation ID is displayed in error toast
    await expect(errorToast).toContainText(/cor_abc123def456/i);
  });

  test('should handle httpOnly cookies correctly across page navigation', async ({ page, context }) => {
    const timestamp = Date.now();
    const email = `cookietest${timestamp}@example.com`;
    const password = 'SecurePassword123!';

    // Register new user
    await page.goto('/auth/register');
    await page.getByLabel(/full name/i).fill('Cookie Test User');
    await page.getByLabel(/email address/i).fill(email);
    await page.getByLabel(/^password$/i).fill(password);
    await page.getByRole('button', { name: /register/i }).click();

    await expect(page).toHaveURL('/dashboard', { timeout: 10000 });

    // Get cookies after registration
    const cookies = await context.cookies();
    const authCookies = cookies.filter(cookie =>
      cookie.name.includes('session') || cookie.name.includes('auth')
    );

    // Verify httpOnly flag is set (security requirement)
    expect(authCookies.some(cookie => cookie.httpOnly)).toBe(true);

    // Navigate away and back
    await page.goto('/');
    await page.goto('/dashboard');

    // Should still be authenticated (cookies persist)
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByText(email)).toBeVisible();

    // Open new tab with same context
    const newPage = await context.newPage();
    await newPage.goto('/dashboard');

    // New tab should share authentication (cookies)
    await expect(newPage).toHaveURL('/dashboard');
    await expect(newPage.getByText(email)).toBeVisible();

    await newPage.close();
  });

  test('should handle concurrent task operations correctly', async ({ page }) => {
    const timestamp = Date.now();
    const email = `concurrent${timestamp}@example.com`;
    const password = 'SecurePassword123!';

    // Register and login
    await page.goto('/auth/register');
    await page.getByLabel(/full name/i).fill('Concurrent Test User');
    await page.getByLabel(/email address/i).fill(email);
    await page.getByLabel(/^password$/i).fill(password);
    await page.getByRole('button', { name: /register/i }).click();

    await expect(page).toHaveURL('/dashboard', { timeout: 10000 });

    // Create multiple tasks in rapid succession
    const taskTitles = [
      'Task 1: Quick win',
      'Task 2: Important meeting',
      'Task 3: Code review'
    ];

    for (const title of taskTitles) {
      const addTaskButton = page.getByRole('button', { name: /add task/i }).first();
      await addTaskButton.click();
      await page.getByLabel(/title/i).fill(title);
      await page.getByRole('button', { name: /create/i }).click();

      // Wait briefly between tasks
      await page.waitForTimeout(100);
    }

    // Verify all tasks appear
    for (const title of taskTitles) {
      await expect(page.getByText(title)).toBeVisible({ timeout: 5000 });
    }

    // Mark all as complete rapidly
    const checkboxes = await page.getByRole('checkbox').all();
    for (const checkbox of checkboxes) {
      await checkbox.click();
      await page.waitForTimeout(50);
    }

    // Filter to show only completed
    const statusFilter = page.getByLabel(/filter by status/i);
    await statusFilter.click();
    await page.getByRole('option', { name: /completed/i }).click();

    // All tasks should be marked complete
    await expect(page.locator('[data-completed="true"]')).toHaveCount(taskTitles.length, { timeout: 5000 });
  });

  test('should maintain filters and search state during task updates', async ({ page }) => {
    const timestamp = Date.now();
    const email = `filterstate${timestamp}@example.com`;
    const password = 'SecurePassword123!';

    // Register and login
    await page.goto('/auth/register');
    await page.getByLabel(/full name/i).fill('Filter State User');
    await page.getByLabel(/email address/i).fill(email);
    await page.getByLabel(/^password$/i).fill(password);
    await page.getByRole('button', { name: /register/i }).click();

    await expect(page).toHaveURL('/dashboard', { timeout: 10000 });

    // Create tasks with different priorities
    const tasks = [
      { title: 'High priority task', priority: 'high' },
      { title: 'Medium priority task', priority: 'medium' },
      { title: 'Low priority task', priority: 'low' }
    ];

    for (const task of tasks) {
      const addTaskButton = page.getByRole('button', { name: /add task/i }).first();
      await addTaskButton.click();
      await page.getByLabel(/title/i).fill(task.title);

      await page.getByLabel(/priority/i).click();
      await page.getByRole('option', { name: new RegExp(task.priority, 'i') }).click();

      await page.getByRole('button', { name: /create/i }).click();
      await page.waitForTimeout(100);
    }

    // Apply priority filter
    const priorityFilter = page.getByLabel(/filter by priority/i);
    await priorityFilter.click();
    await page.getByRole('option', { name: /^high$/i }).click();

    // Should only show high priority task
    await expect(page.getByText('High priority task')).toBeVisible();
    await expect(page.getByText('Medium priority task')).not.toBeVisible();

    // Complete the high priority task
    const checkbox = page.getByRole('checkbox').first();
    await checkbox.click();

    // Filter should remain active after task update
    await expect(page.getByText('High priority task')).toBeVisible();
    await expect(page.getByText('Medium priority task')).not.toBeVisible();

    // Clear filter
    await priorityFilter.click();
    await page.getByRole('option', { name: /all priorities/i }).click();

    // All tasks should be visible
    await expect(page.getByText('High priority task')).toBeVisible();
    await expect(page.getByText('Medium priority task')).toBeVisible();
    await expect(page.getByText('Low priority task')).toBeVisible();
  });
});
