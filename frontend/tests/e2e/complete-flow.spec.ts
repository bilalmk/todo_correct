/**
 * E2E tests for complete authentication flow (T122-T126)
 * Following building-nextjs-apps E2E patterns
 */
import { test, expect } from '@playwright/test';

test.describe('Complete Authentication Flow', () => {
  test('should complete full user journey: register → login → logout → login (T126)', async ({ page }) => {
    const timestamp = Date.now();
    const email = `journey${timestamp}@example.com`;
    const password = 'testpassword123';
    const name = 'Journey User';

    // Step 1: Register
    await page.goto('/auth/register');
    await page.getByLabel(/full name/i).fill(name);
    await page.getByLabel(/email address/i).fill(email);
    await page.getByLabel(/^password$/i).fill(password);
    await page.getByRole('button', { name: /register/i }).click();

    // Verify redirect to dashboard
    await expect(page).toHaveURL('/dashboard', { timeout: 10000 });
    await expect(page.getByText(/welcome/i)).toBeVisible();

    // Step 2: Logout
    await page.getByRole('button', { name: /sign out/i }).click();

    // Verify redirect to login
    await expect(page).toHaveURL('/auth/login', { timeout: 5000 });

    // Step 3: Login with same credentials
    await page.getByLabel(/email address/i).fill(email);
    await page.getByLabel(/password/i).fill(password);
    await page.getByRole('button', { name: /sign in/i }).click();

    // Verify redirect to dashboard
    await expect(page).toHaveURL('/dashboard', { timeout: 10000 });
    await expect(page.getByText(/welcome/i)).toBeVisible();
    await expect(page.getByText(email)).toBeVisible();

    // Step 4: Logout again
    await page.getByRole('button', { name: /sign out/i }).click();

    // Verify final redirect to login
    await expect(page).toHaveURL('/auth/login', { timeout: 5000 });
  });

  test('should complete login flow with correct credentials (T122)', async ({ page, context }) => {
    const timestamp = Date.now();
    const email = `login${timestamp}@example.com`;
    const password = 'testpassword123';

    // First register a user
    await page.goto('/auth/register');
    await page.getByLabel(/full name/i).fill('Login Test User');
    await page.getByLabel(/email address/i).fill(email);
    await page.getByLabel(/^password$/i).fill(password);
    await page.getByRole('button', { name: /register/i }).click();
    await page.waitForURL('/dashboard', { timeout: 10000 });

    // Logout
    await page.getByRole('button', { name: /sign out/i }).click();
    await page.waitForURL('/auth/login', { timeout: 5000 });

    // Now test login flow
    await page.getByLabel(/email address/i).fill(email);
    await page.getByLabel(/password/i).fill(password);
    await page.getByRole('button', { name: /sign in/i }).click();

    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard', { timeout: 10000 });
    await expect(page.getByText(email)).toBeVisible();

    // Verify session is stored (cookies)
    const cookies = await context.cookies();
    expect(cookies.length).toBeGreaterThan(0);
  });

  test('should show error for wrong password (T123)', async ({ page }) => {
    const timestamp = Date.now();
    const email = `wrongpwd${timestamp}@example.com`;

    // First register a user
    await page.goto('/auth/register');
    await page.getByLabel(/full name/i).fill('Wrong Password User');
    await page.getByLabel(/email address/i).fill(email);
    await page.getByLabel(/^password$/i).fill('correctpassword');
    await page.getByRole('button', { name: /register/i }).click();
    await page.waitForURL('/dashboard', { timeout: 10000 });

    // Logout
    await page.getByRole('button', { name: /sign out/i }).click();
    await page.waitForURL('/auth/login', { timeout: 5000 });

    // Try to login with wrong password
    await page.getByLabel(/email address/i).fill(email);
    await page.getByLabel(/password/i).fill('wrongpassword');
    await page.getByRole('button', { name: /sign in/i }).click();

    // Should show error
    await expect(page.getByText(/invalid.*password/i)).toBeVisible();
    await expect(page).toHaveURL('/auth/login');
  });

  test('should show error for non-existent user (T123)', async ({ page }) => {
    await page.goto('/auth/login');

    await page.getByLabel(/email address/i).fill('nonexistent@example.com');
    await page.getByLabel(/password/i).fill('somepassword');
    await page.getByRole('button', { name: /sign in/i }).click();

    // Should show error (same as wrong password for security)
    await expect(page.getByText(/invalid.*password/i)).toBeVisible();
    await expect(page).toHaveURL('/auth/login');
  });

  test('should complete logout flow (T124)', async ({ page, context }) => {
    const timestamp = Date.now();
    const email = `logout${timestamp}@example.com`;

    // Register and login
    await page.goto('/auth/register');
    await page.getByLabel(/full name/i).fill('Logout Test User');
    await page.getByLabel(/email address/i).fill(email);
    await page.getByLabel(/^password$/i).fill('testpassword123');
    await page.getByRole('button', { name: /register/i }).click();
    await page.waitForURL('/dashboard', { timeout: 10000 });

    // Get cookies before logout
    const cookiesBefore = await context.cookies();
    expect(cookiesBefore.length).toBeGreaterThan(0);

    // Click logout
    await page.getByRole('button', { name: /sign out/i }).click();

    // Should redirect to login
    await expect(page).toHaveURL('/auth/login', { timeout: 5000 });

    // Verify cookies are cleared/invalidated
    const cookiesAfter = await context.cookies();
    // Better Auth may keep some cookies but session should be invalid

    // Try to access dashboard without authentication
    await page.goto('/dashboard');

    // Should redirect back to login
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 5000 });
  });

  test('should redirect unauthenticated users from protected routes (T125)', async ({ page }) => {
    // Try to access dashboard without logging in
    await page.goto('/dashboard');

    // Should redirect to login
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 5000 });
  });

  test('should redirect authenticated users away from auth pages (T125)', async ({ page }) => {
    const timestamp = Date.now();
    const email = `authredirect${timestamp}@example.com`;

    // Register and login
    await page.goto('/auth/register');
    await page.getByLabel(/full name/i).fill('Auth Redirect User');
    await page.getByLabel(/email address/i).fill(email);
    await page.getByLabel(/^password$/i).fill('testpassword123');
    await page.getByRole('button', { name: /register/i }).click();
    await page.waitForURL('/dashboard', { timeout: 10000 });

    // Try to access login page while authenticated
    await page.goto('/auth/login');

    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard', { timeout: 5000 });

    // Try to access register page while authenticated
    await page.goto('/auth/register');

    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard', { timeout: 5000 });
  });

  test('should have accessible navigation (T125)', async ({ page }) => {
    const timestamp = Date.now();
    const email = `accessible${timestamp}@example.com`;

    // Register
    await page.goto('/auth/register');
    await page.getByLabel(/full name/i).fill('Accessible User');
    await page.getByLabel(/email address/i).fill(email);
    await page.getByLabel(/^password$/i).fill('testpassword123');
    await page.getByRole('button', { name: /register/i }).click();
    await page.waitForURL('/dashboard', { timeout: 10000 });

    // Check logout button is accessible
    const logoutButton = page.getByRole('button', { name: /sign out/i });
    await expect(logoutButton).toBeVisible();
    await expect(logoutButton).toBeEnabled();

    // Verify button has proper attributes
    await expect(logoutButton).toHaveAttribute('type', 'button');
  });
});
