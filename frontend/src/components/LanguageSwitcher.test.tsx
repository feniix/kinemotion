import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { vi } from 'vitest'
import LanguageSwitcher from './LanguageSwitcher'

// Mock the useLanguage hook
vi.mock('../hooks/useLanguage', () => ({
  useLanguage: vi.fn(() => ({
    t: (key: string, options?: Record<string, unknown>) => {
      const translations: Record<string, string> = {
        'languageSwitcher.english': 'English',
        'languageSwitcher.spanish': 'Español',
        'languageSwitcher.french': 'Français',
      }
      return translations[key] || key
    },
    changeLanguage: vi.fn(),
    currentLanguage: 'en',
    availableLanguages: [
      { code: 'en', label: 'English' },
      { code: 'es', label: 'Español' },
      { code: 'fr', label: 'Français' },
    ],
  })),
}))

import { useLanguage } from '../hooks/useLanguage'

describe('LanguageSwitcher', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders a select dropdown with language options', () => {
    render(<LanguageSwitcher />)

    const select = screen.getByRole('combobox')
    expect(select).toBeInTheDocument()
  })

  it('displays all available languages as options', () => {
    render(<LanguageSwitcher />)

    expect(screen.getByText('English')).toBeInTheDocument()
    expect(screen.getByText('Español')).toBeInTheDocument()
    expect(screen.getByText('Français')).toBeInTheDocument()
  })

  it('has aria-label for accessibility', () => {
    render(<LanguageSwitcher />)

    const select = screen.getByRole('combobox', { name: /select language/i })
    expect(select).toBeInTheDocument()
  })

  it('has title attribute for tooltip', () => {
    render(<LanguageSwitcher />)

    const select = screen.getByRole('combobox')
    expect(select).toHaveAttribute('title', 'Change application language')
  })

  it('calls changeLanguage when a new language is selected', async () => {
    const mockChangeLanguage = vi.fn()
    vi.mocked(useLanguage).mockReturnValue({
      t: vi.fn((key: string) => {
        const translations: Record<string, string> = {
          'languageSwitcher.english': 'English',
          'languageSwitcher.spanish': 'Español',
          'languageSwitcher.french': 'Français',
        }
        return translations[key] || key
      }),
      changeLanguage: mockChangeLanguage,
      currentLanguage: 'en',
      availableLanguages: [
        { code: 'en', label: 'English' },
        { code: 'es', label: 'Español' },
        { code: 'fr', label: 'Français' },
      ],
    })

    render(<LanguageSwitcher />)

    const select = screen.getByRole('combobox')
    fireEvent.change(select, { target: { value: 'es' } })

    expect(mockChangeLanguage).toHaveBeenCalledWith('es')
  })

  it('displays the current language as selected', () => {
    vi.mocked(useLanguage).mockReturnValue({
      t: vi.fn((key: string) => {
        const translations: Record<string, string> = {
          'languageSwitcher.english': 'English',
          'languageSwitcher.spanish': 'Español',
          'languageSwitcher.french': 'Français',
        }
        return translations[key] || key
      }),
      changeLanguage: vi.fn(),
      currentLanguage: 'es',
      availableLanguages: [
        { code: 'en', label: 'English' },
        { code: 'es', label: 'Español' },
        { code: 'fr', label: 'Français' },
      ],
    })

    render(<LanguageSwitcher />)

    const select = screen.getByRole('combobox') as HTMLSelectElement
    expect(select.value).toBe('es')
  })

  it('supports switching between all available languages', async () => {
    const mockChangeLanguage = vi.fn()
    vi.mocked(useLanguage).mockReturnValue({
      t: vi.fn((key: string) => {
        const translations: Record<string, string> = {
          'languageSwitcher.english': 'English',
          'languageSwitcher.spanish': 'Español',
          'languageSwitcher.french': 'Français',
        }
        return translations[key] || key
      }),
      changeLanguage: mockChangeLanguage,
      currentLanguage: 'en',
      availableLanguages: [
        { code: 'en', label: 'English' },
        { code: 'es', label: 'Español' },
        { code: 'fr', label: 'Français' },
      ],
    })

    render(<LanguageSwitcher />)

    const select = screen.getByRole('combobox')

    // Switch to Spanish
    fireEvent.change(select, { target: { value: 'es' } })
    expect(mockChangeLanguage).toHaveBeenCalledWith('es')

    // Switch to French
    fireEvent.change(select, { target: { value: 'fr' } })
    expect(mockChangeLanguage).toHaveBeenCalledWith('fr')

    // Switch back to English
    fireEvent.change(select, { target: { value: 'en' } })
    expect(mockChangeLanguage).toHaveBeenCalledWith('en')

    expect(mockChangeLanguage).toHaveBeenCalledTimes(3)
  })

  it('applies correct CSS class', () => {
    render(<LanguageSwitcher />)

    const container = screen.getByRole('combobox').parentElement
    expect(container).toHaveClass('language-switcher')
  })

  it('select element has correct CSS class', () => {
    render(<LanguageSwitcher />)

    const select = screen.getByRole('combobox')
    expect(select).toHaveClass('language-select')
  })
})
