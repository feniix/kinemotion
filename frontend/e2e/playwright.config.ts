import { defineConfig, devices } from '@playwright/test'
import { resolve } from 'path'
import { fileURLToPath } from 'url'

const __dirname = fileURLToPath(new URL('.', import.meta.url))

/**
 * Playwright E2E Configuration for Kinemotion
 *
 * Environment: Production (https://kinemotion.vercel.app)
 * Auth: Session reuse via storageState (saved Supabase session)
 *
 * Session Setup (one-time, manual):
 *   npx playwright codegen --save-storage=e2e/.auth/prod-user.json https://kinemotion.vercel.app
 *   - Complete Google OAuth login
 *   - Verify you're logged in (see your email)
 *   - Close browser (Ctrl+C)
 */
export default defineConfig({
  // Use absolute path to tests directory
  testDir: resolve(__dirname, './tests'),

  fullyParallel: false, // Run sequentially for now (can parallelize later)
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1, // Single worker to avoid rate limiting
  reporter: [
    ['html', { open: 'never', outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results.json' }],
    ['list'],
  ],
  timeout: 60_000, // 60s timeout (video uploads can be slow)

  use: {
    baseURL: 'https://kinemotion.vercel.app',
    trace: 'retain-on-failure', // Capture trace on failure
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    // Add Firefox and Safari when needed
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },
    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },
  ],

  // Output directories (relative to config file)
  outputDir: 'test-results',
})
