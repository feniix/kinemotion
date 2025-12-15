import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ErrorBoundary from './ErrorBoundary'
import { useLanguage } from '../hooks/useLanguage'

vi.mock('../hooks/useLanguage')

// Component that throws an error
const ThrowError = () => {
  throw new Error('Test error message')
}

// Component that doesn't throw
const SafeComponent = () => <div>Safe content</div>

describe('ErrorBoundary', () => {
  const mockT = vi.fn((key: string) => {
    const translations: Record<string, string> = {
      'errorBoundary.heading': 'Something went wrong',
      'errorBoundary.message': 'An unexpected error occurred. Please try refreshing the page or contact support if the issue persists.',
      'errorBoundary.details': 'Error Details',
      'errorBoundary.retryButton': 'Try Again'
    }
    return translations[key] || key
  })

  beforeEach(() => {
    vi.clearAllMocks()
    ;(useLanguage as any).mockReturnValue({
      t: mockT,
      changeLanguage: vi.fn(),
      currentLanguage: 'en',
      availableLanguages: []
    })
    // Suppress console.error for error boundary tests
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('should render children when no error', () => {
    render(
      <ErrorBoundary>
        <SafeComponent />
      </ErrorBoundary>
    )

    expect(screen.getByText('Safe content')).toBeInTheDocument()
  })

  it('should render error message when error is caught', () => {
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    )

    expect(mockT).toHaveBeenCalledWith('errorBoundary.heading')
    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
  })

  it('should display error description', () => {
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    )

    expect(mockT).toHaveBeenCalledWith('errorBoundary.message')
    expect(
      screen.getByText(
        'An unexpected error occurred. Please try refreshing the page or contact support if the issue persists.'
      )
    ).toBeInTheDocument()
  })

  it('should display error details section', () => {
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    )

    expect(mockT).toHaveBeenCalledWith('errorBoundary.details')
    expect(screen.getByText('Error Details')).toBeInTheDocument()
  })

  it('should show actual error message in details', () => {
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    )

    expect(screen.getByText('Test error message')).toBeInTheDocument()
  })

  it('should display retry button with translation', () => {
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    )

    expect(mockT).toHaveBeenCalledWith('errorBoundary.retryButton')
    expect(screen.getByRole('button', { name: 'Try Again' })).toBeInTheDocument()
  })

  it('should reset error state when retry button clicked', async () => {
    const user = userEvent.setup()
    let shouldThrow = true

    const ConditionalError = () => {
      if (shouldThrow) {
        throw new Error('Test error')
      }
      return <div>Safe content</div>
    }

    const { rerender } = render(
      <ErrorBoundary>
        <ConditionalError />
      </ErrorBoundary>
    )

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()

    shouldThrow = false
    const retryButton = screen.getByRole('button', { name: 'Try Again' })
    await user.click(retryButton)

    rerender(
      <ErrorBoundary>
        <ConditionalError />
      </ErrorBoundary>
    )

    expect(screen.getByText('Safe content')).toBeInTheDocument()
  })

  it('should display error icon', () => {
    const { container } = render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    )

    const errorIcon = container.querySelector('.error-icon')
    expect(errorIcon).toBeInTheDocument()
    expect(errorIcon).toHaveTextContent('🔧')
  })

  it('should have error-boundary container class', () => {
    const { container } = render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    )

    expect(container.querySelector('.error-boundary')).toBeInTheDocument()
  })

  it('should have error-details element for expanding error info', () => {
    const { container } = render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    )

    const details = container.querySelector('.error-details')
    expect(details).toBeInTheDocument()
  })

  it('should render error message in pre tag', () => {
    const { container } = render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    )

    const preTag = container.querySelector('.error-details pre')
    expect(preTag).toBeInTheDocument()
    expect(preTag).toHaveTextContent('Test error message')
  })

  it('should call all translation functions', () => {
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    )

    expect(mockT).toHaveBeenCalledWith('errorBoundary.heading')
    expect(mockT).toHaveBeenCalledWith('errorBoundary.message')
    expect(mockT).toHaveBeenCalledWith('errorBoundary.details')
    expect(mockT).toHaveBeenCalledWith('errorBoundary.retryButton')
  })

  it('should maintain error state across re-renders', async () => {
    const { rerender } = render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    )

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()

    rerender(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    )

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
  })

  it('should handle different error messages', () => {
    const CustomError = () => {
      throw new Error('Custom error message specific to situation')
    }

    render(
      <ErrorBoundary>
        <CustomError />
      </ErrorBoundary>
    )

    expect(screen.getByText('Custom error message specific to situation')).toBeInTheDocument()
  })
})
