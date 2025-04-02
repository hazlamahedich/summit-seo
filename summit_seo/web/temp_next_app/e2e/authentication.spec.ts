import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('shows login form on login page', async ({ page }) => {
    // Navigate to the login page
    await page.goto('/login');
    
    // Expect to see the login form
    const emailInput = page.getByLabel('Email');
    const passwordInput = page.getByLabel('Password');
    const loginButton = page.getByRole('button', { name: 'Sign In' });
    
    await expect(emailInput).toBeVisible();
    await expect(passwordInput).toBeVisible();
    await expect(loginButton).toBeVisible();
  });

  test('shows error message with invalid credentials', async ({ page }) => {
    // Navigate to the login page
    await page.goto('/login');
    
    // Fill in the form with invalid credentials
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByLabel('Password').fill('wrongpassword');
    
    // Submit the form
    await page.getByRole('button', { name: 'Sign In' }).click();
    
    // Expect to see an error message
    await expect(page.getByText(/invalid email or password/i)).toBeVisible({ timeout: 5000 });
  });

  test('redirects to dashboard after successful login', async ({ page }) => {
    // Navigate to the login page
    await page.goto('/login');
    
    // Fill in the form with valid test credentials (these would need to exist in the test environment)
    await page.getByLabel('Email').fill('test-user@example.com');
    await page.getByLabel('Password').fill('test-password-123');
    
    // Submit the form
    await page.getByRole('button', { name: 'Sign In' }).click();
    
    // Expect to be redirected to the dashboard
    await expect(page).toHaveURL(/.*dashboard/, { timeout: 5000 });
    await expect(page.getByText(/welcome to your dashboard/i)).toBeVisible();
  });

  test('allows user to sign up', async ({ page }) => {
    // Navigate to the signup page
    await page.goto('/signup');
    
    // Generate a unique email for this test
    const uniqueEmail = `test-${Date.now()}@example.com`;
    
    // Fill in the form with test credentials
    await page.getByLabel('Email').fill(uniqueEmail);
    await page.getByLabel('Password').fill('Test123!@#');
    await page.getByLabel(/confirm password/i).fill('Test123!@#');
    
    // Submit the form
    await page.getByRole('button', { name: /sign up|register|create account/i }).click();
    
    // Expect to see a success message or be redirected
    await expect(page).toHaveURL(/.*verification|.*dashboard/, { timeout: 5000 });
  });

  test('allows password reset request', async ({ page }) => {
    // Navigate to the password reset page
    await page.goto('/forgot-password');
    
    // Fill in the email
    await page.getByLabel('Email').fill('test@example.com');
    
    // Submit the form
    await page.getByRole('button', { name: /reset password|send instructions/i }).click();
    
    // Expect to see a confirmation message
    await expect(page.getByText(/instructions sent|check your email/i)).toBeVisible({ timeout: 5000 });
  });

  test('allows user to logout', async ({ page }) => {
    // First login
    await page.goto('/login');
    await page.getByLabel('Email').fill('test-user@example.com');
    await page.getByLabel('Password').fill('test-password-123');
    await page.getByRole('button', { name: 'Sign In' }).click();
    
    // Wait for dashboard to load
    await expect(page).toHaveURL(/.*dashboard/, { timeout: 5000 });
    
    // Click on user menu and logout
    await page.getByText('test-user@example.com').click();
    await page.getByRole('menuitem', { name: /log out|sign out/i }).click();
    
    // Expect to be redirected to the login page
    await expect(page).toHaveURL(/\/$|\/login/, { timeout: 5000 });
  });
}); 