import { test, expect } from '@playwright/test'
import { ensureSignedIn } from './auth-utils'

/**
 * Results Display Tests
 *
 * These tests verify the results display after analysis.
 * Since we can't easily trigger a real analysis in CI,
 * these tests focus on the UI structure and assume
 * we have a way to mock or trigger results.
 *
 * For full testing, consider:
 * 1. Using a pre-recorded backend response (mocking)
 * 2. Having a dedicated test video that processes quickly
 * 3. Using Playwright's API mocking to inject results
 */

test.describe('Results Display', () => {
  test.beforeEach(async ({ page }) => {
    await ensureSignedIn(page)
  })

  test('displays metrics after successful analysis', async ({ page }) => {
    // This test would need actual analysis to complete
    // For now, we test the structure by triggering a mock response

    // Mock the analyze endpoint to return sample data
    await page.route('**/api/analyze', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status_code: 200,
          message: 'Analysis complete',
          metrics: {
            data: {
              jump_height_m: 0.45,
              flight_time_ms: 605,
              countermovement_depth_m: 0.32,
              peak_concentric_velocity_m_s: 3.2,
            },
            validation: {
              status: 'PASS',
              issues: [],
            },
          },
          processing_time_s: 2.5,
        }),
      })
    })

    // Select and "upload" a file
    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles({
      name: 'test.mp4',
      mimeType: 'video/mp4',
      buffer: Buffer.from('mock'),
    })

    // Click analyze
    await page.locator('.analyze-hero-button').click()

    // Should show results
    await expect(page.locator('.results-container')).toBeVisible({ timeout: 10_000 })

    // Check for key elements
    await expect(page.locator('.kpi-grid')).toBeVisible()
    await expect(page.locator('.phase-card')).toHaveCount(3) // Loading, Explosion, Outcome
  })

  test('shows validation status banner', async ({ page }) => {
    // Mock response with validation warnings
    await page.route('**/api/analyze', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status_code: 200,
          message: 'Analysis complete with warnings',
          metrics: {
            data: { jump_height_m: 0.35 },
            validation: {
              status: 'PASS_WITH_WARNINGS',
              issues: [
                {
                  severity: 'WARNING',
                  message: 'Low visibility in some frames',
                },
              ],
            },
          },
          processing_time_s: 1.8,
        }),
      })
    })

    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles({
      name: 'test.mp4',
      mimeType: 'video/mp4',
      buffer: Buffer.from('mock'),
    })

    await page.locator('.analyze-hero-button').click()

    // Should show validation banner
    await expect(page.locator('.validation-banner')).toBeVisible()
    await expect(page.locator('.validation-banner')).toContainText('PASS WITH WARNINGS')
    await expect(page.locator('.issue-warning')).toContainText('Low visibility')
  })

  test('shows error display on failure', async ({ page }) => {
    // Mock an error response
    await page.route('**/api/analyze', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Internal server error',
          message: 'Video processing failed',
        }),
      })
    })

    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles({
      name: 'test.mp4',
      mimeType: 'video/mp4',
      buffer: Buffer.from('mock'),
    })

    await page.locator('.analyze-hero-button').click()

    // Should show error display
    await expect(page.locator('.error-display')).toBeVisible()
    // The error display shows "Analysis Failed" heading
    await expect(page.locator('.error-display')).toContainText('Analysis Failed')
    await expect(page.locator('.error-display')).toContainText('Internal server error')

    // Should have retry button (text may be "Try Again")
    const retryButton = page.locator('button:has-text("Retry"), button:has-text("Try Again")')
    await expect(retryButton).toBeVisible()
  })

  test('displays CMJ metrics correctly', async ({ page }) => {
    await page.route('**/api/analyze', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status_code: 200,
          message: 'Analysis complete',
          metrics: {
            data: {
              jump_height_m: 0.42,
              flight_time_ms: 585,
              countermovement_depth_m: 0.28,
              peak_concentric_velocity_m_s: 2.9,
              concentric_duration_ms: 350,
              eccentric_duration_ms: 420,
            },
            validation: { status: 'PASS', issues: [] },
          },
          processing_time_s: 2.1,
        }),
      })
    })

    // Select CMJ
    await page.locator('button:has-text("CMJ")').click()

    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles({
      name: 'test.mp4',
      mimeType: 'video/mp4',
      buffer: Buffer.from('mock'),
    })

    await page.locator('.analyze-hero-button').click()

    await expect(page.locator('.results-container')).toBeVisible()

    // Check CMJ-specific metrics are displayed
    await expect(page.locator('.kpi-grid')).toBeVisible()
    await expect(page.locator('text=/Jump Height/i')).toBeVisible()
    // Note: The UI uses "Air Time" not "Flight Time"
    await expect(page.locator('text=/Air Time/i')).toBeVisible()
    // "Depth" is shown in the timeline phase cards (countermovement depth)
    await expect(page.locator('text=/Depth/i')).toBeVisible()
  })

  test('displays Drop Jump metrics correctly', async ({ page }) => {
    await page.route('**/api/analyze', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status_code: 200,
          message: 'Analysis complete',
          metrics: {
            data: {
              jump_height_m: 0.38,
              reactive_strength_index: 1.2,
              ground_contact_time_ms: 245,
              flight_time_ms: 555,
            },
            validation: { status: 'PASS', issues: [] },
          },
          processing_time_s: 1.9,
        }),
      })
    })

    // Select Drop Jump
    await page.locator('button:has-text("Drop Jump")').click()

    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles({
      name: 'test.mp4',
      mimeType: 'video/mp4',
      buffer: Buffer.from('mock'),
    })

    await page.locator('.analyze-hero-button').click()

    await expect(page.locator('.results-container')).toBeVisible()

    // Check Drop Jump-specific metrics are displayed
    await expect(page.locator('.kpi-grid')).toBeVisible()
    await expect(page.locator('text=/RSI/i')).toBeVisible()
    await expect(page.locator('text=/Contact Time/i')).toBeVisible()
  })

  test('shows processing time in results', async ({ page }) => {
    await page.route('**/api/analyze', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status_code: 200,
          message: 'Analysis complete',
          metrics: {
            data: { jump_height_m: 0.40 },
            validation: { status: 'PASS', issues: [] },
          },
          processing_time_s: 3.14,
        }),
      })
    })

    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles({
      name: 'test.mp4',
      mimeType: 'video/mp4',
      buffer: Buffer.from('mock'),
    })

    await page.locator('.analyze-hero-button').click()

    await expect(page.locator('.results-container')).toBeVisible()

    // Should show processing time
    await expect(page.locator('.meta-tag')).toContainText(/3\.1s/)
  })

  test('can reset and upload another video', async ({ page }) => {
    // First analysis
    await page.route('**/api/analyze', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status_code: 200,
          metrics: { data: { jump_height_m: 0.40 }, validation: { status: 'PASS', issues: [] } },
          processing_time_s: 2.0,
        }),
      })
    })

    // Upload and analyze
    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles({
      name: 'test.mp4',
      mimeType: 'video/mp4',
      buffer: Buffer.from('mock'),
    })
    await page.locator('.analyze-hero-button').click()
    await expect(page.locator('.results-container')).toBeVisible()

    // Reset (would need to trigger reset via UI or page refresh)
    await page.reload()

    // Should show upload form again
    await expect(page.locator('.upload-controller')).toBeVisible()
    await expect(page.locator('.analyze-hero-button')).toBeDisabled()
  })
})
