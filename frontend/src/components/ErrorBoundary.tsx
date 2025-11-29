import { Component, ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
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
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <div className="error-icon">🔧</div>
          <h2>Something went wrong</h2>
          <p className="error-message">
            An unexpected error occurred. Please try refreshing the page or contact support if the issue persists.
          </p>
          <details className="error-details">
            <summary>Error Details</summary>
            <pre>{this.state.error?.message}</pre>
          </details>
          <button onClick={this.handleReset} className="retry-button">
            Try Again
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
