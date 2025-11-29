interface ErrorDisplayProps {
  error: string
  onRetry?: () => void
}

function ErrorDisplay({ error, onRetry }: ErrorDisplayProps) {
  // Map technical errors to user-friendly messages
  const getUserFriendlyMessage = (errorMsg: string): string => {
    if (errorMsg.includes('Failed to fetch') || errorMsg.includes('NetworkError')) {
      return 'Unable to connect to the analysis server. Please check your internet connection and try again.'
    }

    if (errorMsg.includes('500') || errorMsg.includes('Internal Server Error')) {
      return 'Server error occurred during analysis. Please try again or contact support if the issue persists.'
    }

    if (errorMsg.includes('413') || errorMsg.includes('too large')) {
      return 'Video file is too large. Please use a video smaller than 500MB.'
    }

    if (errorMsg.includes('400') || errorMsg.includes('Bad Request')) {
      return 'Invalid video file or request. Please ensure you selected a valid video file.'
    }

    if (errorMsg.includes('timeout')) {
      return 'Analysis took too long. Please try with a shorter video or try again later.'
    }

    // Return the original error if it's already user-friendly
    return errorMsg
  }

  return (
    <div className="error-display" role="alert" aria-live="assertive">
      <div className="error-icon">⚠️</div>
      <h3>Analysis Failed</h3>
      <p className="error-message">{getUserFriendlyMessage(error)}</p>

      <div className="error-actions">
        {onRetry && (
          <button onClick={onRetry} className="retry-button">
            Try Again
          </button>
        )}
      </div>

      <p className="error-help">
        If this problem persists, please contact support with the following information:
      </p>
      <details className="error-details">
        <summary>Technical Details</summary>
        <pre>{error}</pre>
      </details>
    </div>
  )
}

export default ErrorDisplay
