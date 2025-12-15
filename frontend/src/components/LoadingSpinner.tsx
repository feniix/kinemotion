import { useLanguage } from '../hooks/useLanguage'

interface LoadingSpinnerProps {
  uploadProgress: number
}

function LoadingSpinner({ uploadProgress }: LoadingSpinnerProps) {
  const { t } = useLanguage()
  const isUploading = uploadProgress > 0 && uploadProgress < 100
  const isProcessing = uploadProgress >= 100

  const headingText = isUploading ? t('loading.uploadingVideo') : t('loading.analyzingVideo')
  const messageText = isUploading
    ? t('loading.uploadProgress', { progress: uploadProgress })
    : t('loading.estimatedTime')

  return (
    <div className="loading-spinner" role="status" aria-live="polite" aria-busy="true">
      <div className="spinner" aria-label="Loading indicator"></div>
      <h3>{headingText}</h3>
      <p className="loading-message" aria-label={messageText}>
        {messageText}
      </p>

      {isUploading && (
        <div
          className="progress-bar"
          role="progressbar"
          aria-valuenow={uploadProgress}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={messageText}
        >
          <div className="progress-fill" style={{ width: `${uploadProgress}%` }}></div>
        </div>
      )}

      <div className="loading-steps">
        <ul>
          <li className={isUploading ? 'active' : 'complete'}>{t('loading.steps.uploading')}</li>
          <li className={isProcessing && uploadProgress >= 100 ? 'active' : ''}>
            {t('loading.steps.processing')}
          </li>
          <li className={isProcessing && uploadProgress >= 100 ? 'active' : ''}>
            {t('loading.steps.detecting')}
          </li>
          <li className={isProcessing && uploadProgress >= 100 ? 'active' : ''}>
            {t('loading.steps.calculating')}
          </li>
        </ul>
      </div>
    </div>
  )
}

export default LoadingSpinner
