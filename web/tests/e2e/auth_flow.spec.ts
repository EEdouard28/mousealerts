/**
 * End-to-end tests for authentication flow
 */
import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto('/auth/login');
  });

  test('should display login page correctly', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/MouseAlerts/);
    
    // Check for phone input
    await expect(page.locator('input[type="tel"]')).toBeVisible();
    
    // Check for submit button
    await expect(page.locator('button[type="submit"]')).toBeVisible();
    
    // Check for demo button
    await expect(page.locator('text=Try Demo Account')).toBeVisible();
  });

  test('should handle phone number input', async ({ page }) => {
    // Test phone number input
    const phoneInput = page.locator('input[type="tel"]');
    await phoneInput.fill('+15551234567');
    await expect(phoneInput).toHaveValue('+15551234567');
  });

  test('should validate phone number format', async ({ page }) => {
    // Test invalid phone number
    const phoneInput = page.locator('input[type="tel"]');
    await phoneInput.fill('123');
    
    const submitButton = page.locator('button[type="submit"]');
    await submitButton.click();
    
    // Should show validation error
    await expect(page.locator('text=Invalid phone number')).toBeVisible();
  });

  test('should handle magic link request', async ({ page }) => {
    // Mock API response
    await page.route('**/api/auth/magic-link', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ message: 'Magic link sent successfully' })
      });
    });

    // Fill phone number
    await page.locator('input[type="tel"]').fill('+15551234567');
    
    // Submit form
    await page.locator('button[type="submit"]').click();
    
    // Should show success message
    await expect(page.locator('text=Magic link sent successfully')).toBeVisible();
  });

  test('should handle magic link request failure', async ({ page }) => {
    // Mock API error
    await page.route('**/api/auth/magic-link', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Failed to send SMS' })
      });
    });

    // Fill phone number
    await page.locator('input[type="tel"]').fill('+15551234567');
    
    // Submit form
    await page.locator('button[type="submit"]').click();
    
    // Should show error message
    await expect(page.locator('text=Failed to send SMS')).toBeVisible();
  });

  test('should handle demo account setup', async ({ page }) => {
    // Click demo account button
    await page.locator('text=Try Demo Account').click();
    
    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    
    // Should show dashboard content
    await expect(page.locator('text=Welcome to MouseAlerts')).toBeVisible();
  });

  test('should handle token verification', async ({ page }) => {
    // Mock API response for token verification
    await page.route('**/api/auth/verify*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'mock-jwt-token',
          user: {
            id: 'test-user-id',
            email: 'test@mousealerts.com',
            phone: '+15551234567',
            plan: 'free'
          }
        })
      });
    });

    // Navigate to verify page with token
    await page.goto('/auth/verify?token=test-token');
    
    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
  });

  test('should handle invalid token', async ({ page }) => {
    // Mock API error for invalid token
    await page.route('**/api/auth/verify*', async route => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Invalid or expired token' })
      });
    });

    // Navigate to verify page with invalid token
    await page.goto('/auth/verify?token=invalid-token');
    
    // Should show error message
    await expect(page.locator('text=Invalid or expired token')).toBeVisible();
  });

  test('should handle logout', async ({ page }) => {
    // Set up authenticated state
    await page.addInitScript(() => {
      localStorage.setItem('token', 'mock-jwt-token');
      localStorage.setItem('user', JSON.stringify({
        id: 'test-user-id',
        email: 'test@mousealerts.com',
        phone: '+15551234567',
        plan: 'free'
      }));
    });

    // Navigate to dashboard
    await page.goto('/dashboard');
    
    // Click logout button
    await page.locator('text=Logout').click();
    
    // Should redirect to login page
    await expect(page).toHaveURL('/auth/login');
    
    // Should clear authentication data
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeNull();
  });

  test('should handle protected routes', async ({ page }) => {
    // Try to access protected route without authentication
    await page.goto('/dashboard');
    
    // Should redirect to login page
    await expect(page).toHaveURL('/auth/login');
  });

  test('should handle authentication persistence', async ({ page }) => {
    // Set up authenticated state
    await page.addInitScript(() => {
      localStorage.setItem('token', 'mock-jwt-token');
      localStorage.setItem('user', JSON.stringify({
        id: 'test-user-id',
        email: 'test@mousealerts.com',
        phone: '+15551234567',
        plan: 'free'
      }));
    });

    // Navigate to dashboard
    await page.goto('/dashboard');
    
    // Should show dashboard content
    await expect(page.locator('text=Welcome to MouseAlerts')).toBeVisible();
    
    // Refresh page
    await page.reload();
    
    // Should still be authenticated
    await expect(page.locator('text=Welcome to MouseAlerts')).toBeVisible();
  });

  test('should handle authentication expiration', async ({ page }) => {
    // Set up expired authentication
    await page.addInitScript(() => {
      localStorage.setItem('token', 'expired-jwt-token');
      localStorage.setItem('user', JSON.stringify({
        id: 'test-user-id',
        email: 'test@mousealerts.com',
        phone: '+15551234567',
        plan: 'free'
      }));
    });

    // Mock API error for expired token
    await page.route('**/api/me', async route => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Token expired' })
      });
    });

    // Navigate to dashboard
    await page.goto('/dashboard');
    
    // Should redirect to login page
    await expect(page).toHaveURL('/auth/login');
  });

  test('should handle network errors', async ({ page }) => {
    // Mock network error
    await page.route('**/api/auth/magic-link', async route => {
      await route.abort('failed');
    });

    // Fill phone number
    await page.locator('input[type="tel"]').fill('+15551234567');
    
    // Submit form
    await page.locator('button[type="submit"]').click();
    
    // Should show network error message
    await expect(page.locator('text=Network error')).toBeVisible();
  });

  test('should handle loading states', async ({ page }) => {
    // Mock slow API response
    await page.route('**/api/auth/magic-link', async route => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ message: 'Magic link sent successfully' })
      });
    });

    // Fill phone number
    await page.locator('input[type="tel"]').fill('+15551234567');
    
    // Submit form
    await page.locator('button[type="submit"]').click();
    
    // Should show loading state
    await expect(page.locator('text=Sending...')).toBeVisible();
    
    // Should show success message after loading
    await expect(page.locator('text=Magic link sent successfully')).toBeVisible();
  });
});
