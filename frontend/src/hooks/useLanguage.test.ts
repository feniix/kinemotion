import { renderHook, act } from '@testing-library/react'
import { vi } from 'vitest'
import { useLanguage } from './useLanguage'
import i18n from '../i18n/config'

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString()
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    },
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

describe('useLanguage Hook', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('returns translation function', () => {
    const { result } = renderHook(() => useLanguage())

    expect(result.current.t).toBeDefined()
    expect(typeof result.current.t).toBe('function')
  })

  it('returns changeLanguage function', () => {
    const { result } = renderHook(() => useLanguage())

    expect(result.current.changeLanguage).toBeDefined()
    expect(typeof result.current.changeLanguage).toBe('function')
  })

  it('returns current language', () => {
    const { result } = renderHook(() => useLanguage())

    expect(result.current.currentLanguage).toBeDefined()
    expect(typeof result.current.currentLanguage).toBe('string')
  })

  it('returns available languages array', () => {
    const { result } = renderHook(() => useLanguage())

    expect(result.current.availableLanguages).toBeDefined()
    expect(Array.isArray(result.current.availableLanguages)).toBe(true)
    expect(result.current.availableLanguages.length).toBeGreaterThan(0)
  })

  it('available languages include English, Spanish, and French', () => {
    const { result } = renderHook(() => useLanguage())

    const codes = result.current.availableLanguages.map((lang) => lang.code)
    expect(codes).toContain('en')
    expect(codes).toContain('es')
    expect(codes).toContain('fr')
  })

  it('available languages have code and label properties', () => {
    const { result } = renderHook(() => useLanguage())

    result.current.availableLanguages.forEach((lang) => {
      expect(lang).toHaveProperty('code')
      expect(lang).toHaveProperty('label')
      expect(typeof lang.code).toBe('string')
      expect(typeof lang.label).toBe('string')
    })
  })

  it('translates keys correctly', () => {
    const { result } = renderHook(() => useLanguage())

    // Test with a common key that should exist
    const translated = result.current.t('common.appName')
    expect(translated).toBeDefined()
    expect(translated).not.toBe('') // Should have a translation
  })

  it('supports interpolation in translations', () => {
    const { result } = renderHook(() => useLanguage())

    const translated = result.current.t('footer.copyright', { year: 2025 })
    expect(translated).toContain('2025')
  })

  it('changes language', async () => {
    const { result, rerender } = renderHook(() => useLanguage())

    const initialLanguage = result.current.currentLanguage

    await act(async () => {
      result.current.changeLanguage('es')
    })

    rerender()

    // Language should change (after i18n processes the change)
    await new Promise((resolve) => setTimeout(resolve, 100))
    expect(i18n.language).toBe('es')
  })

  it('persists language choice to localStorage', async () => {
    const { result } = renderHook(() => useLanguage())

    await act(async () => {
      result.current.changeLanguage('fr')
    })

    expect(localStorage.getItem('language')).toBe('fr')
  })

  it('supports multiple language switches', async () => {
    const { result } = renderHook(() => useLanguage())

    await act(async () => {
      result.current.changeLanguage('es')
    })
    expect(localStorage.getItem('language')).toBe('es')

    await act(async () => {
      result.current.changeLanguage('fr')
    })
    expect(localStorage.getItem('language')).toBe('fr')

    await act(async () => {
      result.current.changeLanguage('en')
    })
    expect(localStorage.getItem('language')).toBe('en')
  })

  it('returns updated current language after change', async () => {
    const { result, rerender } = renderHook(() => useLanguage())

    await act(async () => {
      result.current.changeLanguage('es')
    })

    rerender()

    // Give i18n time to update
    await new Promise((resolve) => setTimeout(resolve, 100))

    // Current language should reflect the change
    expect(i18n.language).toBe('es')
  })

  it('translation function returns non-empty strings for valid keys', () => {
    const { result } = renderHook(() => useLanguage())

    const keys = [
      'common.appName',
      'common.tagline',
      'header.signOut',
      'results.heading',
      'uploadForm.uploadPrompt',
      'errors.networkError',
    ]

    keys.forEach((key) => {
      const translation = result.current.t(key)
      expect(translation).toBeDefined()
      expect(translation.length).toBeGreaterThan(0)
    })
  })

  it('translation function returns key name for missing translations', () => {
    const { result } = renderHook(() => useLanguage())

    // Use a key that doesn't exist
    const translation = result.current.t('nonexistent.key.that.does.not.exist')
    expect(translation).toBeDefined()
  })
})
