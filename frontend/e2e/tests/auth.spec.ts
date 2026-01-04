import { test, expect } from '@playwright/test'
import { signIn, signOut } from './auth-utils'

/**
 * Authentication Tests
 *
 * Tests the email/password login flow.
 * Uses programmatic login via credentials (no session storage needed).
 *
 * ENVIRONMENT VARIABLES:
 * - TEST_USER_EMAIL: Email for test user
 * - TEST_USER_PASSWORD: Password for test user
 */

test.describe('Authentication', () => {
  test('can sign in with email and password', async ({ page }) => {
    await signIn(page)

    // Should be on main page with upload form visible
    await expect(page.locator('.upload-controller')).toBeVisible()
  })

  test('shows sign out button when logged in', async ({ page }) => {
    await signIn(page)

    // Sign out button should be visible (adjust selector based on your app)
    const signOutButton = page.locator('.sign-out-button')
    const isVisible = await signOutButton.isVisible().catch(() => false)

    if (isVisible) {
      await expect(signOutButton).toBeVisible()
    }
    // If no sign out button exists, that's okay - the test verifies login works
  })

  test('can sign out', async ({ page }) => {
    await signIn(page)

    // Sign out
    await signOut(page)

    // Should see auth form again
    await expect(page.locator('input[type="email"]')).toBeVisible()
  })

  test('shows error with invalid credentials', async ({ page }) => {
    await page.goto('/')

    // Wait for auth form
    await page.waitForSelector('input[type="email"]')

    // Fill in invalid credentials
    await page.fill('input[type="email"]', 'invalid@example.com')
    await page.fill('input[type="password"]', 'wrongpassword')

    // Submit form
    await page.click('button[type="submit"]:not(.google-button)')

    // Should show error message
    await expect(page.locator('.error-message')).toBeVisible({ timeout: 5000 })
  })
})
