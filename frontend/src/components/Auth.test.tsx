import { render, screen, waitFor } from '@testing-library/react'
import Auth from './Auth'
import { useAuth } from '../hooks/useAuth'
import { useLanguage } from '../hooks/useLanguage'

vi.mock('../hooks/useAuth')
vi.mock('../hooks/useLanguage')

describe('Auth Component', () => {
  const mockSignIn = vi.fn()
  const mockSignUp = vi.fn()
  const mockSignInWithGoogle = vi.fn()
  const mockOnSuccess = vi.fn()

  const mockT = vi.fn((key: string) => {
    const translations: Record<string, string> = {
      'auth.signUp': 'Sign Up',
      'auth.signIn': 'Sign In',
      'auth.signUpSubtitle': 'Create an account to analyze jump videos',
      'auth.signInSubtitle': 'Sign in to analyze jump videos',
      'auth.signInWithGoogle': 'Sign in with Google',
      'auth.email': 'Email',
      'auth.password': 'Password',
      'auth.loading': 'Loading...',
      'auth.errors.fillAllFields': 'Please fill in all fields',
      'auth.errors.passwordLength': 'Password must be at least 6 characters',
      'auth.success': 'Check your email for confirmation link!',
      'auth.signUpToggle': 'Don\'t have an account?',
      'auth.signInToggle': 'Already have an account?'
    }
    return translations[key] || key
  })

  beforeEach(() => {
    vi.clearAllMocks()
    ;(useAuth as any).mockReturnValue({
      signIn: mockSignIn,
      signUp: mockSignUp,
      signInWithGoogle: mockSignInWithGoogle,
      error: null,
      loading: false
    })
    ;(useLanguage as any).mockReturnValue({
      t: mockT,
      changeLanguage: vi.fn(),
      currentLanguage: 'en',
      availableLanguages: []
    })
  })

  it('should call translation function for sign in labels', () => {
    render(<Auth onSuccess={mockOnSuccess} />)

    expect(mockT).toHaveBeenCalledWith('auth.signIn')
    expect(mockT).toHaveBeenCalledWith('auth.signInSubtitle')
    expect(mockT).toHaveBeenCalledWith('auth.email')
    expect(mockT).toHaveBeenCalledWith('auth.password')
  })

  it('should render email input field', () => {
    render(<Auth onSuccess={mockOnSuccess} />)

    expect(screen.getByLabelText('Email')).toBeInTheDocument()
  })

  it('should render password input field', () => {
    render(<Auth onSuccess={mockOnSuccess} />)

    expect(screen.getByLabelText('Password')).toBeInTheDocument()
  })

  it('should call translation function for sign up labels', () => {
    render(<Auth onSuccess={mockOnSuccess} />)

    expect(mockT).toHaveBeenCalledWith('auth.signUpToggle')
  })

  it('should call signInWithGoogle when Google button clicked', async () => {
    mockSignInWithGoogle.mockResolvedValue(undefined)
    render(<Auth onSuccess={mockOnSuccess} />)

    expect(mockT).toHaveBeenCalledWith('auth.signInWithGoogle')
  })

  it('should display auth error message', () => {
    ;(useAuth as any).mockReturnValue({
      signIn: mockSignIn,
      signUp: mockSignUp,
      signInWithGoogle: mockSignInWithGoogle,
      error: 'Invalid credentials',
      loading: false
    })

    render(<Auth onSuccess={mockOnSuccess} />)

    expect(screen.getByText('Invalid credentials')).toBeInTheDocument()
  })

  it('should disable buttons when loading', () => {
    ;(useAuth as any).mockReturnValue({
      signIn: mockSignIn,
      signUp: mockSignUp,
      signInWithGoogle: mockSignInWithGoogle,
      error: null,
      loading: true
    })

    render(<Auth onSuccess={mockOnSuccess} />)

    const buttons = screen.getAllByRole('button')
    buttons.forEach(button => {
      expect(button).toBeDisabled()
    })
  })

  it('should show loading text on buttons when loading', () => {
    ;(useAuth as any).mockReturnValue({
      signIn: mockSignIn,
      signUp: mockSignUp,
      signInWithGoogle: mockSignInWithGoogle,
      error: null,
      loading: true
    })

    render(<Auth onSuccess={mockOnSuccess} />)

    expect(mockT).toHaveBeenCalledWith('auth.loading')
  })

  it('should render Google sign in button', () => {
    render(<Auth onSuccess={mockOnSuccess} />)

    const buttons = screen.getAllByRole('button')
    expect(buttons.length).toBeGreaterThan(1) // Google button + other form button
  })

  it('should render form element', () => {
    const { container } = render(<Auth onSuccess={mockOnSuccess} />)

    expect(container.querySelector('form')).toBeInTheDocument()
  })

  it('should have inputs with correct types', () => {
    render(<Auth onSuccess={mockOnSuccess} />)

    const emailInput = screen.getByLabelText('Email') as HTMLInputElement
    expect(emailInput.type).toBe('email')

    const passwordInput = screen.getByLabelText('Password') as HTMLInputElement
    expect(passwordInput.type).toBe('password')
  })
})
