import { Component, ReactNode } from 'react'
import { useLanguage } from '../hooks/useLanguage'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

class ErrorBoundaryImpl extends Component<Props & { t: (key: string) => string }, State> {
  constructor(props: Props & { t: (key: string) => string }) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error) {
    console.error('Error caught by boundary:', error)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null })
  }

  render() {
    const { t } = this.props

    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <div className="error-icon">🔧</div>
          <h2>{t('errorBoundary.heading')}</h2>
          <p className="error-message">
            {t('errorBoundary.message')}
          </p>
          <details className="error-details">
            <summary>{t('errorBoundary.details')}</summary>
            <pre>{this.state.error?.message}</pre>
          </details>
          <button onClick={this.handleReset} className="retry-button">
            {t('errorBoundary.retryButton')}
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

function ErrorBoundary({ children }: Props) {
  const { t } = useLanguage()

  return (
    <ErrorBoundaryImpl t={t}>
      {children}
    </ErrorBoundaryImpl>
  )
}

export default ErrorBoundary
