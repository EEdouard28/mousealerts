/**
 * End-to-end tests for alert creation flow
 */
import { test, expect } from '@playwright/test';

test.describe('Alert Creation Flow', () => {
  test.beforeEach(async ({ page }) => {
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

    // Navigate to alert creation page
    await page.goto('/alerts/create');
  });

  test('should display alert creation form', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/Create Alert/);
    
    // Check for restaurant search
    await expect(page.locator('input[placeholder*="restaurant"]')).toBeVisible();
    
    // Check for date picker
    await expect(page.locator('input[type="date"]')).toBeVisible();
    
    // Check for time inputs
    await expect(page.locator('input[type="time"]')).toHaveCount(2);
    
    // Check for party size input
    await expect(page.locator('input[type="number"]')).toBeVisible();
    
    // Check for notification channels
    await expect(page.locator('input[type="checkbox"]')).toHaveCount(3);
    
    // Check for submit button
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should handle restaurant search', async ({ page }) => {
    // Test restaurant search
    const restaurantInput = page.locator('input[placeholder*="restaurant"]');
    await restaurantInput.fill('Cinderella');
    
    // Should show search results
    await expect(page.locator('text=Cinderella\'s Royal Table')).toBeVisible();
    
    // Click on search result
    await page.locator('text=Cinderella\'s Royal Table').click();
    
    // Should populate the input
    await expect(restaurantInput).toHaveValue('Cinderella\'s Royal Table');
  });

  test('should handle date selection', async ({ page }) => {
    // Test date selection
    const dateInput = page.locator('input[type="date"]');
    await dateInput.fill('2024-12-25');
    await expect(dateInput).toHaveValue('2024-12-25');
  });

  test('should handle time selection', async ({ page }) => {
    // Test time selection
    const timeInputs = page.locator('input[type="time"]');
    await timeInputs.nth(0).fill('18:00');
    await timeInputs.nth(1).fill('20:00');
    
    await expect(timeInputs.nth(0)).toHaveValue('18:00');
    await expect(timeInputs.nth(1)).toHaveValue('20:00');
  });

  test('should handle party size input', async ({ page }) => {
    // Test party size input
    const partySizeInput = page.locator('input[type="number"]');
    await partySizeInput.fill('4');
    await expect(partySizeInput).toHaveValue('4');
  });

  test('should handle notification channel selection', async ({ page }) => {
    // Test notification channel selection
    const emailCheckbox = page.locator('input[type="checkbox"]').nth(0);
    const smsCheckbox = page.locator('input[type="checkbox"]').nth(1);
    const pushCheckbox = page.locator('input[type="checkbox"]').nth(2);
    
    // Select email and SMS
    await emailCheckbox.check();
    await smsCheckbox.check();
    
    await expect(emailCheckbox).toBeChecked();
    await expect(smsCheckbox).toBeChecked();
    await expect(pushCheckbox).not.toBeChecked();
  });

  test('should validate required fields', async ({ page }) => {
    // Try to submit without filling required fields
    await page.locator('button[type="submit"]').click();
    
    // Should show validation errors
    await expect(page.locator('text=Restaurant is required')).toBeVisible();
    await expect(page.locator('text=Date is required')).toBeVisible();
    await expect(page.locator('text=Party size is required')).toBeVisible();
  });

  test('should validate date format', async ({ page }) => {
    // Test invalid date
    const dateInput = page.locator('input[type="date"]');
    await dateInput.fill('invalid-date');
    
    await page.locator('button[type="submit"]').click();
    
    // Should show validation error
    await expect(page.locator('text=Invalid date')).toBeVisible();
  });

  test('should validate time format', async ({ page }) => {
    // Test invalid time
    const timeInputs = page.locator('input[type="time"]');
    await timeInputs.nth(0).fill('25:00');
    
    await page.locator('button[type="submit"]').click();
    
    // Should show validation error
    await expect(page.locator('text=Invalid time')).toBeVisible();
  });

  test('should validate party size', async ({ page }) => {
    // Test invalid party size
    const partySizeInput = page.locator('input[type="number"]');
    await partySizeInput.fill('0');
    
    await page.locator('button[type="submit"]').click();
    
    // Should show validation error
    await expect(page.locator('text=Party size must be at least 1')).toBeVisible();
  });

  test('should create alert successfully', async ({ page }) => {
    // Mock API response
    await page.route('**/api/alerts', async route => {
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'test-alert-id',
          restaurant: 'Cinderella\'s Royal Table',
          date: '2024-12-25',
          time_start: '18:00',
          time_end: '20:00',
          party_size: 4,
          status: 'active'
        })
      });
    });

    // Fill form
    await page.locator('input[placeholder*="restaurant"]').fill('Cinderella\'s Royal Table');
    await page.locator('input[type="date"]').fill('2024-12-25');
    await page.locator('input[type="time"]').nth(0).fill('18:00');
    await page.locator('input[type="time"]').nth(1).fill('20:00');
    await page.locator('input[type="number"]').fill('4');
    await page.locator('input[type="checkbox"]').nth(0).check();
    
    // Submit form
    await page.locator('button[type="submit"]').click();
    
    // Should show success message
    await expect(page.locator('text=Alert created successfully')).toBeVisible();
    
    // Should redirect to alerts page
    await expect(page).toHaveURL('/alerts');
  });

  test('should handle alert creation failure', async ({ page }) => {
    // Mock API error
    await page.route('**/api/alerts', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Failed to create alert' })
      });
    });

    // Fill form
    await page.locator('input[placeholder*="restaurant"]').fill('Cinderella\'s Royal Table');
    await page.locator('input[type="date"]').fill('2024-12-25');
    await page.locator('input[type="time"]').nth(0).fill('18:00');
    await page.locator('input[type="time"]').nth(1).fill('20:00');
    await page.locator('input[type="number"]').fill('4');
    
    // Submit form
    await page.locator('button[type="submit"]').click();
    
    // Should show error message
    await expect(page.locator('text=Failed to create alert')).toBeVisible();
  });

  test('should handle plan limits', async ({ page }) => {
    // Set up user with plan limits
    await page.addInitScript(() => {
      localStorage.setItem('user', JSON.stringify({
        id: 'test-user-id',
        email: 'test@mousealerts.com',
        phone: '+15551234567',
        plan: 'free'
      }));
    });

    // Mock API response for plan limits
    await page.route('**/api/alerts/plan-info', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          plan_id: 'free',
          plan_name: 'Free',
          limits: {
            alerts_per_user: 2,
            notification_channels: ['email'],
            instant_notifications: false,
            ai_prompt_bar: false,
            priority_support: false,
            monitoring_interval: 300
          },
          usage: {
            total_alerts: 2,
            active_alerts: 2,
            paused_alerts: 0,
            expired_alerts: 0
          }
        })
      });
    });

    // Navigate to alert creation page
    await page.goto('/alerts/create');
    
    // Should show plan limit warning
    await expect(page.locator('text=You have reached your alert limit')).toBeVisible();
    
    // Should show upgrade suggestion
    await expect(page.locator('text=Upgrade to Premium')).toBeVisible();
  });

  test('should handle loading states', async ({ page }) => {
    // Mock slow API response
    await page.route('**/api/alerts', async route => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'test-alert-id',
          restaurant: 'Cinderella\'s Royal Table',
          date: '2024-12-25',
          time_start: '18:00',
          time_end: '20:00',
          party_size: 4,
          status: 'active'
        })
      });
    });

    // Fill form
    await page.locator('input[placeholder*="restaurant"]').fill('Cinderella\'s Royal Table');
    await page.locator('input[type="date"]').fill('2024-12-25');
    await page.locator('input[type="time"]').nth(0).fill('18:00');
    await page.locator('input[type="time"]').nth(1).fill('20:00');
    await page.locator('input[type="number"]').fill('4');
    
    // Submit form
    await page.locator('button[type="submit"]').click();
    
    // Should show loading state
    await expect(page.locator('text=Creating alert...')).toBeVisible();
    
    // Should show success message after loading
    await expect(page.locator('text=Alert created successfully')).toBeVisible();
  });

  test('should handle form reset', async ({ page }) => {
    // Fill form
    await page.locator('input[placeholder*="restaurant"]').fill('Cinderella\'s Royal Table');
    await page.locator('input[type="date"]').fill('2024-12-25');
    await page.locator('input[type="time"]').nth(0).fill('18:00');
    await page.locator('input[type="time"]').nth(1).fill('20:00');
    await page.locator('input[type="number"]').fill('4');
    
    // Click reset button
    await page.locator('button[type="reset"]').click();
    
    // Should clear all fields
    await expect(page.locator('input[placeholder*="restaurant"]')).toHaveValue('');
    await expect(page.locator('input[type="date"]')).toHaveValue('');
    await expect(page.locator('input[type="time"]').nth(0)).toHaveValue('');
    await expect(page.locator('input[type="time"]').nth(1)).toHaveValue('');
    await expect(page.locator('input[type="number"]')).toHaveValue('');
  });

  test('should handle keyboard navigation', async ({ page }) => {
    // Test tab navigation
    await page.keyboard.press('Tab');
    await expect(page.locator('input[placeholder*="restaurant"]')).toBeFocused();
    
    await page.keyboard.press('Tab');
    await expect(page.locator('input[type="date"]')).toBeFocused();
    
    await page.keyboard.press('Tab');
    await expect(page.locator('input[type="time"]').nth(0)).toBeFocused();
  });

  test('should handle mobile viewport', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check that form is still usable on mobile
    await expect(page.locator('input[placeholder*="restaurant"]')).toBeVisible();
    await expect(page.locator('input[type="date"]')).toBeVisible();
    await expect(page.locator('input[type="time"]')).toHaveCount(2);
    await expect(page.locator('input[type="number"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should handle accessibility', async ({ page }) => {
    // Check for proper labels
    await expect(page.locator('label[for*="restaurant"]')).toBeVisible();
    await expect(page.locator('label[for*="date"]')).toBeVisible();
    await expect(page.locator('label[for*="time"]')).toBeVisible();
    await expect(page.locator('label[for*="party-size"]')).toBeVisible();
    
    // Check for proper ARIA attributes
    await expect(page.locator('input[placeholder*="restaurant"]')).toHaveAttribute('aria-label');
    await expect(page.locator('input[type="date"]')).toHaveAttribute('aria-label');
    await expect(page.locator('input[type="time"]').nth(0)).toHaveAttribute('aria-label');
    await expect(page.locator('input[type="time"]').nth(1)).toHaveAttribute('aria-label');
    await expect(page.locator('input[type="number"]')).toHaveAttribute('aria-label');
  });
});
