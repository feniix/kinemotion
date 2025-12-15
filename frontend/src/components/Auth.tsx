/**
 * Authentication component for sign in/sign up
 */

import { useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { useLanguage } from '../hooks/useLanguage'

interface AuthProps {
  onSuccess?: () => void
}

export default function Auth({ onSuccess }: AuthProps) {
  const { t } = useLanguage()
  const [isSignUp, setIsSignUp] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [localError, setLocalError] = useState<string | null>(null)
  const { signIn, signUp, signInWithGoogle, error: authError, loading } = useAuth()

  const error = localError || authError

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLocalError(null)

    if (!email || !password) {
      setLocalError(t('auth.errors.fillAllFields'))
      return
    }

    if (password.length < 6) {
      setLocalError(t('auth.errors.passwordLength'))
      return
    }

    try {
      if (isSignUp) {
        await signUp(email, password)
        setLocalError(null)
        alert(t('auth.success'))
      } else {
        await signIn(email, password)
        setLocalError(null)
        onSuccess?.()
      }
    } catch (err) {
      // Error is handled by useAuth hook
      console.error('Auth error:', err)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>{isSignUp ? t('auth.signUp') : t('auth.signIn')}</h2>
        <p className="auth-subtitle">
          {isSignUp ? t('auth.signUpSubtitle') : t('auth.signInSubtitle')}
        </p>

        <button
          type="button"
          onClick={async () => {
            try {
              await signInWithGoogle()
            } catch (err) {
              console.error('Google sign-in error:', err)
            }
          }}
          className="auth-button google-button"
          disabled={loading}
        >
          <svg
            className="google-icon"
            width="18"
            height="18"
            viewBox="0 0 18 18"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.615z"
              fill="#4285F4"
            />
            <path
              d="M9 18c2.43 0 4.467-.806 5.965-2.184l-2.908-2.258c-.806.54-1.837.86-3.057.86-2.35 0-4.34-1.587-5.053-3.72H.957v2.332C2.438 15.983 5.482 18 9 18z"
              fill="#34A853"
            />
            <path
              d="M3.947 10.698c-.18-.54-.282-1.117-.282-1.698s.102-1.158.282-1.698V4.97H.957C.348 6.175 0 7.55 0 9s.348 2.825.957 4.03l2.99-2.332z"
              fill="#FBBC05"
            />
            <path
              d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0 5.482 0 2.438 2.017.957 4.97L3.947 7.302C4.66 5.167 6.65 3.58 9 3.58z"
              fill="#EA4335"
            />
          </svg>
          {t('auth.signInWithGoogle')}
        </button>

        <div className="auth-divider">
          <span>or</span>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">{t('auth.email')}</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">{t('auth.password')}</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              minLength={6}
              required
              disabled={loading}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button
            type="submit"
            className="auth-button"
            disabled={loading}
          >
            {loading ? t('auth.loading') : isSignUp ? t('auth.signUp') : t('auth.signIn')}
          </button>
        </form>

        <div className="auth-toggle">
          {isSignUp ? t('auth.signInToggle') : t('auth.signUpToggle')}{' '}
          <button
            onClick={() => {
              setIsSignUp(!isSignUp)
              setLocalError(null)
            }}
            className="toggle-button"
            disabled={loading}
          >
            {isSignUp ? t('auth.signIn') : t('auth.signUp')}
          </button>
        </div>
      </div>
    </div>
  )
}
