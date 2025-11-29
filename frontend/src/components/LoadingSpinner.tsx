interface LoadingSpinnerProps {
  uploadProgress: number
}

function LoadingSpinner({ uploadProgress }: LoadingSpinnerProps) {
  const isUploading = uploadProgress > 0 && uploadProgress < 100
  const isProcessing = uploadProgress >= 100

  return (
    <div className="loading-spinner" role="status" aria-live="polite" aria-busy="true">
      <div className="spinner" aria-label="Loading indicator"></div>
      <h3>{isUploading ? 'Uploading Video' : 'Analyzing Video'}</h3>
      <p className="loading-message" aria-label={isUploading ? `Upload progress: ${uploadProgress}%` : 'Video analysis in progress'}>
        {isUploading
          ? `Upload progress: ${uploadProgress}%`
          : 'This typically takes 10-60 seconds depending on video length'}
      </p>

      {isUploading && (
        <div
          className="progress-bar"
          role="progressbar"
          aria-valuenow={uploadProgress}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`Upload progress: ${uploadProgress}%`}
        >
          <div className="progress-fill" style={{ width: `${uploadProgress}%` }}></div>
        </div>
      )}

      <div className="loading-steps">
        <ul>
          <li className={isUploading ? 'active' : 'complete'}>Uploading video</li>
          <li className={isProcessing && uploadProgress >= 100 ? 'active' : ''}>
            Processing video frames
          </li>
          <li className={isProcessing && uploadProgress >= 100 ? 'active' : ''}>
            Detecting pose landmarks
          </li>
          <li className={isProcessing && uploadProgress >= 100 ? 'active' : ''}>
            Calculating jump metrics
          </li>
        </ul>
      </div>
    </div>
  )
}

export default LoadingSpinner
