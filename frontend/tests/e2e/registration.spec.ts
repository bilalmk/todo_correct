/**
 * E2E tests for user registration flow (T120-T121)
 * Following building-nextjs-apps testing patterns with Playwright
 */
import { test, expect } from '@playwright/test';

test.describe('User Registration', () => {
  test('should complete registration flow successfully (T120)', async ({ page }) => {
    // Navigate to registration page
    await page.goto('/auth/register');

    // Verify page loaded
    await expect(page).toHaveTitle(/Todo Evolution/);
    await expect(page.getByRole('heading', { name: /create account/i })).toBeVisible();

    // Fill registration form
    const timestamp = Date.now();
    await page.getByLabel(/full name/i).fill('Test User');
    await page.getByLabel(/email address/i).fill(`test${timestamp}@example.com`);
    await page.getByLabel(/^password$/i).fill('testpassword123');

    // Submit form
    await page.getByRole('button', { name: /register/i }).click();

    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard', { timeout: 10000 });

    // Verify dashboard shows user info
    await expect(page.getByText(/welcome/i)).toBeVisible();
    await expect(page.getByText(`test${timestamp}@example.com`)).toBeVisible();
  });

  test('should show error for duplicate email (T121)', async ({ page }) => {
    // First, register a user
    const timestamp = Date.now();
    const email = `duplicate${timestamp}@example.com`;

    await page.goto('/auth/register');
    await page.getByLabel(/full name/i).fill('First User');
    await page.getByLabel(/email address/i).fill(email);
    await page.getByLabel(/^password$/i).fill('testpassword123');
    await page.getByRole('button', { name: /register/i }).click();

    // Wait for redirect to dashboard
    await page.waitForURL('/dashboard', { timeout: 10000 });

    // Logout
    await page.getByRole('button', { name: /sign out/i }).click();
    await page.waitForURL('/auth/login', { timeout: 5000 });

    // Try to register again with same email
    await page.goto('/auth/register');
    await page.getByLabel(/full name/i).fill('Second User');
    await page.getByLabel(/email address/i).fill(email);
    await page.getByLabel(/^password$/i).fill('testpassword123');
    await page.getByRole('button', { name: /register/i }).click();

    // Should show error message
    await expect(page.getByText(/already registered/i)).toBeVisible();

    // Should remain on registration page
    await expect(page).toHaveURL('/auth/register');
  });

  test('should show error for invalid email format (T121)', async ({ page }) => {
    await page.goto('/auth/register');

    await page.getByLabel(/full name/i).fill('Test User');
    await page.getByLabel(/email address/i).fill('invalid-email');
    await page.getByLabel(/^password$/i).fill('testpassword123');
    await page.getByRole('button', { name: /register/i }).click();

    // Should show validation error
    await expect(page.getByText(/invalid.*email/i)).toBeVisible();
  });

  test('should show error for short password (T121)', async ({ page }) => {
    await page.goto('/auth/register');

    await page.getByLabel(/full name/i).fill('Test User');
    await page.getByLabel(/email address/i).fill('test@example.com');
    await page.getByLabel(/^password$/i).fill('short');
    await page.getByRole('button', { name: /register/i }).click();

    // Should show validation error
    await expect(page.getByText(/at least 8 characters/i)).toBeVisible();
  });

  test('should show error for empty name (T121)', async ({ page }) => {
    await page.goto('/auth/register');

    await page.getByLabel(/email address/i).fill('test@example.com');
    await page.getByLabel(/^password$/i).fill('testpassword123');
    await page.getByRole('button', { name: /register/i }).click();

    // Should show validation error for name
    await expect(page.getByText(/name.*required/i)).toBeVisible();
  });

  test('should have accessible form fields (T121)', async ({ page }) => {
    await page.goto('/auth/register');

    // Check ARIA attributes
    const nameInput = page.getByLabel(/full name/i);
    const emailInput = page.getByLabel(/email address/i);
    const passwordInput = page.getByLabel(/^password$/i);

    await expect(nameInput).toHaveAttribute('id');
    await expect(emailInput).toHaveAttribute('id');
    await expect(passwordInput).toHaveAttribute('id');

    // Check labels are associated
    await expect(nameInput).toBeVisible();
    await expect(emailInput).toBeVisible();
    await expect(passwordInput).toBeVisible();
  });
});
