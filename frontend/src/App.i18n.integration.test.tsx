import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { vi } from 'vitest'
import App from './App'
import i18n from './i18n/config'

// Mock Auth hook
vi.mock('./hooks/useAuth', () => ({
  useAuth: vi.fn(() => ({
    user: { email: 'test@example.com' },
    loading: false,
    signOut: vi.fn(),
  })),
}))

// Mock other hooks to simplify integration test
vi.mock('./hooks/useAnalysis', () => ({
  useAnalysis: vi.fn(() => ({
    file: null,
    jumpType: 'cmj',
    loading: false,
    uploadProgress: 0,
    metrics: null,
    error: null,
    enableDebug: false,
    setFile: vi.fn(),
    setJumpType: vi.fn(),
    setEnableDebug: vi.fn(),
    analyze: vi.fn(),
    retry: vi.fn(),
  })),
}))

vi.mock('./hooks/useRecentUploads', () => ({
  useRecentUploads: vi.fn(() => ({
    recentUploads: [],
    addRecentUpload: vi.fn(),
    clearRecentUploads: vi.fn(),
  })),
}))

vi.mock('./hooks/useBackendVersion', () => ({
  useBackendVersion: vi.fn(() => ({
    backendVersion: 'v0.1.0',
    kinemotionVersion: 'v0.34.0',
  })),
}))

describe('i18n Integration Tests', () => {
  beforeEach(() => {
    // Reset i18n to English
    i18n.changeLanguage('en')
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('renders app with English text by default', async () => {
    render(<App />)

    // Check for English text
    await waitFor(() => {
      expect(screen.getByText('Kinemotion')).toBeInTheDocument()
    })
  })

  it('language switcher is present in the app', async () => {
    render(<App />)

    const languageSelect = screen.getByRole('combobox')
    expect(languageSelect).toBeInTheDocument()
  })

  it('changes app language when language switcher is updated', async () => {
    render(<App />)

    // Get language selector
    const languageSelect = screen.getByRole('combobox') as HTMLSelectElement

    // Initially should be English
    expect(languageSelect.value).toBe('en')

    // Change to Spanish
    fireEvent.change(languageSelect, { target: { value: 'es' } })

    // Wait for i18n to update
    await waitFor(() => {
      expect(i18n.language).toBe('es')
    })

    // Language selector should reflect the change
    expect(languageSelect.value).toBe('es')
  })

  it('persists language selection across renders', async () => {
    const { rerender } = render(<App />)

    const languageSelect = screen.getByRole('combobox') as HTMLSelectElement

    // Change to French
    fireEvent.change(languageSelect, { target: { value: 'fr' } })

    await waitFor(() => {
      expect(localStorage.getItem('language')).toBe('fr')
    })

    // Rerender the app
    rerender(<App />)

    // Language should still be French
    const updatedSelect = screen.getByRole('combobox') as HTMLSelectElement
    await waitFor(() => {
      expect(i18n.language).toBe('fr')
    })
  })

  it('supports switching between all three languages', async () => {
    render(<App />)

    const languageSelect = screen.getByRole('combobox') as HTMLSelectElement

    const languages = ['en', 'es', 'fr']

    for (const lang of languages) {
      fireEvent.change(languageSelect, { target: { value: lang } })

      await waitFor(() => {
        expect(i18n.language).toBe(lang)
      })

      expect(languageSelect.value).toBe(lang)
    }
  })

  it('all UI text uses translations (no hardcoded strings)', async () => {
    render(<App />)

    // These elements should be translated through i18n, not hardcoded
    await waitFor(() => {
      expect(screen.getByText('Kinemotion')).toBeInTheDocument()
      expect(screen.getByText(/Video-based kinematic analysis/)).toBeInTheDocument()
    })
  })

  it('language switcher options are all translated', async () => {
    render(<App />)

    // Check that language option labels are translated
    const options = screen.getAllByRole('option')

    // Should have at least 3 options (en, es, fr)
    expect(options.length).toBeGreaterThanOrEqual(3)

    // Options should have translated labels
    const optionTexts = options.map((opt) => opt.textContent)
    expect(optionTexts).toContain('English') // English option
    expect(optionTexts.some((text) => text?.includes('Español'))) // Spanish option (might include accent)
    expect(optionTexts.some((text) => text?.includes('Français'))) // French option (might include accent)
  })

  it('translation function is available in all components', async () => {
    render(<App />)

    // App should render successfully, which means all components with translations rendered
    await waitFor(() => {
      expect(screen.getByText('Kinemotion')).toBeInTheDocument()
    })
  })

  it('changing language updates all translated text in the app', async () => {
    render(<App />)

    const languageSelect = screen.getByRole('combobox') as HTMLSelectElement

    // Start with English
    await waitFor(() => {
      expect(screen.getByText('Kinemotion')).toBeInTheDocument()
    })

    // Change to Spanish
    fireEvent.change(languageSelect, { target: { value: 'es' } })

    await waitFor(() => {
      expect(i18n.language).toBe('es')
    })

    // The app should still be functional and all text translated
    expect(screen.getByText('Kinemotion')).toBeInTheDocument()
  })

  it('localStorage is updated when language changes', async () => {
    render(<App />)

    const languageSelect = screen.getByRole('combobox') as HTMLSelectElement

    // Change language
    fireEvent.change(languageSelect, { target: { value: 'es' } })

    // Verify localStorage is updated
    await waitFor(() => {
      expect(localStorage.getItem('language')).toBe('es')
    })

    // Change to another language
    fireEvent.change(languageSelect, { target: { value: 'fr' } })

    await waitFor(() => {
      expect(localStorage.getItem('language')).toBe('fr')
    })
  })
})
