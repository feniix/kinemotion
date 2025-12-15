import { useLanguage } from '../hooks/useLanguage'

interface ErrorDisplayProps {
  error: string
  onRetry?: () => void
}

function ErrorDisplay({ error, onRetry }: ErrorDisplayProps) {
  const { t } = useLanguage()

  // Map technical errors to user-friendly messages
  const getUserFriendlyMessage = (errorMsg: string): string => {
    if (errorMsg.includes('Failed to fetch') || errorMsg.includes('NetworkError')) {
      return t('errors.networkError')
    }

    if (errorMsg.includes('500') || errorMsg.includes('Internal Server Error')) {
      return t('errors.serverError')
    }

    if (errorMsg.includes('413') || errorMsg.includes('too large')) {
      return t('errors.fileTooLarge')
    }

    if (errorMsg.includes('400') || errorMsg.includes('Bad Request')) {
      return t('errors.invalidRequest')
    }

    if (errorMsg.includes('timeout')) {
      return t('errors.timeout')
    }

    // Return the original error if it's already user-friendly
    return errorMsg
  }

  return (
    <div className="error-display" role="alert" aria-live="assertive">
      <div className="error-icon">⚠️</div>
      <h3>{t('errors.analysisFailedTitle')}</h3>
      <p className="error-message">{getUserFriendlyMessage(error)}</p>

      <div className="error-actions">
        {onRetry && (
          <button onClick={onRetry} className="retry-button">
            {t('errors.retryButton')}
          </button>
        )}
      </div>

      <p className="error-help">
        {t('errors.contactSupport')}
      </p>
      <details className="error-details">
        <summary>{t('errors.technicalDetails')}</summary>
        <pre>{error}</pre>
      </details>
    </div>
  )
}

export default ErrorDisplay
