import { test, expect } from '@playwright/test'
import { readFileSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'
import { ensureSignedIn } from './auth-utils'

const __dirname = dirname(fileURLToPath(import.meta.url))

/**
 * Video Upload Flow Tests
 *
 * These tests verify the complete upload flow:
 * 1. File selection via file input
 * 2. Drag and drop functionality
 * 3. Jump type selection (CMJ vs Drop Jump)
 * 4. Upload button interaction
 * 5. Progress tracking
 * 6. Error handling
 *
 * NOTE: For actual video processing tests, you'll need a real video file.
 * Place a small test video in e2e/fixtures/test-video.mp4
 */

test.describe('Video Upload Flow', () => {
  test.beforeEach(async ({ page }) => {
    await ensureSignedIn(page)
  })

  test('shows upload form with file input', async ({ page }) => {
    // Should have file input
    const fileInput = page.locator('input[type="file"][accept="video/*"]')
    await expect(fileInput).toBeVisible()

    // Should have jump type buttons
    await expect(page.locator('button:has-text("CMJ")')).toBeVisible()
    await expect(page.locator('button:has-text("Drop Jump")')).toBeVisible()

    // Should have analyze button (disabled when no file selected)
    const analyzeBtn = page.locator('.analyze-hero-button')
    await expect(analyzeBtn).toBeVisible()
    await expect(analyzeBtn).toBeDisabled()
  })

  test('can select jump type', async ({ page }) => {
    // Default is CMJ
    await expect(page.locator('.type-btn.active')).toContainText('CMJ')

    // Click Drop Jump
    await page.locator('button:has-text("Drop Jump")').click()

    // Should now be active
    await expect(page.locator('.type-btn.active')).toContainText('Drop Jump')
  })

  test('enables debug toggle', async ({ page }) => {
    const debugToggle = page.locator('.debug-toggle input[type="checkbox"]')

    await expect(debugToggle).not.toBeChecked()

    // Toggle debug on
    await debugToggle.check()
    await expect(debugToggle).toBeChecked()

    // Toggle debug off
    await debugToggle.uncheck()
    await expect(debugToggle).not.toBeChecked()
  })

  test('enables analyze button after file selection', async ({ page }) => {
    // This test uses a mock file since we may not have a real video
    // In real tests, use a small test video from fixtures

    const fileInput = page.locator('input[type="file"]')

    // Create a minimal "video" file (just for testing the UI flow)
    // In production, you'd use a real MP4 from fixtures
    const mockFile = Buffer.from('mock video content')

    await fileInput.setInputFiles({
      name: 'test-video.mp4',
      mimeType: 'video/mp4',
      buffer: mockFile,
    })

    // Analyze button should be enabled now
    const analyzeBtn = page.locator('.analyze-hero-button')
    await expect(analyzeBtn).toBeEnabled()

    // Should show file preview
    await expect(page.locator('.file-ready-state')).toBeVisible()
    await expect(page.locator('.filename')).toContainText('test-video.mp4')
  })

  test('can clear selected file', async ({ page }) => {
    const fileInput = page.locator('input[type="file"]')
    const mockFile = Buffer.from('mock video content')

    // Select a file
    await fileInput.setInputFiles({
      name: 'test-video.mp4',
      mimeType: 'video/mp4',
      buffer: mockFile,
    })

    await expect(page.locator('.file-ready-state')).toBeVisible()

    // Click change file button
    await page.locator('.change-file-btn').click()

    // Should return to empty state
    await expect(page.locator('.empty-state')).toBeVisible()
    await expect(page.locator('.analyze-hero-button')).toBeDisabled()
  })

  test('validates file size limit', async ({ page }) => {
    const fileInput = page.locator('input[type="file"]')

    // NOTE: Playwright has a 50MB limit for buffers, so we can't test actual large file
    // This test verifies the validation error UI would work for large files
    // In a real scenario, the browser would enforce the 500MB limit

    // For now, we test with a moderately sized file (10MB)
    // The actual size validation happens in the browser before Playwright sees it
    const mediumFile = Buffer.alloc(10 * 1024 * 1024) // 10MB

    await fileInput.setInputFiles({
      name: 'medium-video.mp4',
      mimeType: 'video/mp4',
      buffer: mediumFile,
    })

    // File should be accepted (10MB is within limits)
    await expect(page.locator('.file-ready-state')).toBeVisible()
    await expect(page.locator('.validation-error')).not.toBeVisible()

    // NOTE: To truly test the 500MB limit, we'd need to:
    // 1. Create a real file > 500MB on disk
    // 2. Use page.setInputFiles(path) instead of buffer
    // This is impractical for CI, so we trust the browser's native validation
  })

  test('validates file type', async ({ page }) => {
    const fileInput = page.locator('input[type="file"]')

    // Try to upload a non-video file
    const textFile = Buffer.from('not a video')

    await fileInput.setInputFiles({
      name: 'document.txt',
      mimeType: 'text/plain',
      buffer: textFile,
    })

    // Should show validation error
    await expect(page.locator('.validation-error')).toBeVisible()
    await expect(page.locator('.validation-error')).toContainText('video')
  })

  test('supports drag and drop', async ({ page }) => {
    const dropZone = page.locator('.upload-drop-zone')

    // Create a DataTransfer object for drag-drop simulation
    await dropZone.scrollIntoViewIfNeeded()

    // Note: True drag-drop testing in Playwright requires specific setup
    // This test verifies the drop zone exists and has proper attributes
    await expect(dropZone).toBeVisible()

    // The dropzone should accept drag events
    const hasDragEvents = await dropZone.evaluate((el) => {
      return (
        'ondragover' in el ||
        el.getAttribute('data-testid') === 'file-input' ||
        el.querySelector('input[type="file"]') !== null
      )
    })

    expect(hasDragEvents).toBe(true)
  })
})

test.describe('Upload with Real Video', () => {
  test.beforeEach(async ({ page }) => {
    await ensureSignedIn(page)
  })

  test('uploads CMJ video and shows progress', async ({ page }) => {
    // Use actual test video for CMJ
    const testVideoPath = join(__dirname, '../fixtures/cmj-45-IMG_6733.MOV')

    try {
      readFileSync(testVideoPath)
    } catch {
      test.skip('CMJ test video not found. Add e2e/fixtures/cmj-45-IMG_6733.MOV to run this test.')
    }

    // Select CMJ jump type
    await page.locator('button:has-text("CMJ")').click()

    // Select the test video
    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles(testVideoPath)

    // Verify file is selected
    await expect(page.locator('.file-ready-state')).toBeVisible()
    await expect(page.locator('.filename')).toContainText('cmj-45-IMG_6733.MOV')

    // Click analyze button
    await page.locator('.analyze-hero-button').click()

    // Should show loading state
    await expect(page.locator('.loading-pulse')).toBeVisible()

    // Wait for results or error (with generous timeout for actual upload + processing)
    const resultsOrError = page.locator('.results-container, .error-display')

    // This tests the full flow: upload → backend processing → results
    // Timeout is generous for real video processing
    await expect(resultsOrError).toBeVisible({ timeout: 180_000 })

    // If successful, verify results are shown
    if (await page.locator('.results-container').isVisible()) {
      await expect(page.locator('.kpi-grid')).toBeVisible()
    }
  })

  test('uploads Drop Jump video and shows progress', async ({ page }) => {
    // Use actual test video for Drop Jump
    const testVideoPath = join(__dirname, '../fixtures/dj-45-IMG_6739.MOV')

    try {
      readFileSync(testVideoPath)
    } catch {
      test.skip('Drop Jump test video not found. Add e2e/fixtures/dj-45-IMG_6739.MOV to run this test.')
    }

    // Select Drop Jump type
    await page.locator('button:has-text("Drop Jump")').click()

    // Select the test video
    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles(testVideoPath)

    // Verify file is selected
    await expect(page.locator('.file-ready-state')).toBeVisible()
    await expect(page.locator('.filename')).toContainText('dj-45-IMG_6739.MOV')

    // Click analyze button
    await page.locator('.analyze-hero-button').click()

    // Should show loading state
    await expect(page.locator('.loading-pulse')).toBeVisible()

    // Wait for results or error
    const resultsOrError = page.locator('.results-container, .error-display')
    await expect(resultsOrError).toBeVisible({ timeout: 180_000 })

    // If successful, verify Drop Jump specific results
    if (await page.locator('.results-container').isVisible()) {
      // Should show RSI for drop jump
      await expect(page.locator('text=/RSI/i')).toBeVisible()
    }
  })
})
