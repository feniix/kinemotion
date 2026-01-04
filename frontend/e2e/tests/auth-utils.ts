/**
 * E2E Authentication Helper
 *
 * Handles programmatic login for tests using email/password.
 * Eliminates need for session storage and expired sessions.
 */

import { Page } from '@playwright/test'

const TEST_USER_EMAIL = process.env.TEST_USER_EMAIL || ''
const TEST_USER_PASSWORD = process.env.TEST_USER_PASSWORD || ''

/**
 * Signs in with email/password credentials
 * @param page - Playwright page instance
 */
export async function signIn(page: Page): Promise<void> {
  if (!TEST_USER_EMAIL || !TEST_USER_PASSWORD) {
    throw new Error(
      'TEST_USER_EMAIL and TEST_USER_PASSWORD must be set. ' +
        'Set them in your environment or GitHub Secrets.'
    )
  }

  // Navigate to home (should show auth if not logged in)
  await page.goto('/')

  // Wait for auth form to be visible
  await page.waitForSelector('input[type="email"]', { timeout: 5000 })

  // Fill in credentials
  await page.fill('input[type="email"]', TEST_USER_EMAIL)
  await page.fill('input[type="password"]', TEST_USER_PASSWORD)

  // Submit form
  await page.click('button[type="submit"]:not(.google-button)')

  // Wait for successful login - upload form should appear
  await page.waitForSelector('.upload-controller, .analyze-hero-button', {
    timeout: 10_000,
  })
}

/**
 * Signs out current user
 * @param page - Playwright page instance
 */
export async function signOut(page: Page): Promise<void> {
  // Look for sign out button (should be visible when logged in)
  const signOutButton = page.locator('.sign-out-button, button:has-text("Sign Out")')

  if (await signOutButton.isVisible()) {
    await signOutButton.click()
    // Wait for auth form to reappear
    await page.waitForSelector('input[type="email"]', { timeout: 5000 })
  }
}

/**
 * Ensures user is signed in before test
 * @param page - Playwright page instance
 */
export async function ensureSignedIn(page: Page): Promise<void> {
  await page.goto('/')

  // Check if we're already logged in (upload form is visible)
  const isLoggedIn = await page
    .locator('.upload-controller, .analyze-hero-button')
    .isVisible()
    .catch(() => false)

  if (!isLoggedIn) {
    await signIn(page)
  }
}
