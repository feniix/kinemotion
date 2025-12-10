import { useState } from 'react'
import RecentUploads from './RecentUploads'
import { RecentUpload } from '../hooks/useRecentUploads'

interface UploadFormProps {
  file: File | null
  jumpType: 'cmj' | 'dropjump'
  loading: boolean
  enableDebug: boolean
  recentUploads: RecentUpload[]
  onFileChange: (file: File | null) => void
  onJumpTypeChange: (jumpType: 'cmj' | 'dropjump') => void
  onEnableDebugChange: (enable: boolean) => void
  onAnalyze: () => void
  onClearHistory?: () => void
}

const MAX_FILE_SIZE = 500 * 1024 * 1024 // 500MB

function UploadForm({
  file,
  jumpType,
  loading,
  enableDebug,
  recentUploads,
  onFileChange,
  onJumpTypeChange,
  onEnableDebugChange,
  onAnalyze,
  onClearHistory,
}: UploadFormProps) {
  const [validationError, setValidationError] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)

  const validateFile = (selectedFile: File): boolean => {
    // Validate file size
    if (selectedFile.size > MAX_FILE_SIZE) {
      setValidationError(
        `File size must be less than 500MB. Selected file is ${(selectedFile.size / 1024 / 1024).toFixed(1)}MB`
      )
      return false
    }

    // Validate file type
    if (!selectedFile.type.startsWith('video/')) {
      setValidationError('Please select a valid video file')
      return false
    }

    setValidationError(null)
    return true
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]

    if (!selectedFile) {
      onFileChange(null)
      setValidationError(null)
      return
    }

    if (validateFile(selectedFile)) {
      onFileChange(selectedFile)
    } else {
      e.target.value = '' // Reset input
      onFileChange(null)
    }
  }

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const droppedFile = e.dataTransfer.files?.[0]
    if (!droppedFile) return

    if (validateFile(droppedFile)) {
      onFileChange(droppedFile)
    } else {
      onFileChange(null)
    }
  }

  const handleSelectRecentUpload = (_filename: string, jumpType: 'cmj' | 'dropjump') => {
    onJumpTypeChange(jumpType)
    // Note: We can't actually access the File object from recent history for privacy reasons,
    // so we just set the jump type. The user would need to select the file again.
  }

  return (
    <div className="upload-form">
      <div className="form-group">
        <label htmlFor="video-upload">Select Video</label>
        <div
          className={`upload-drop-zone ${isDragging ? 'dragging' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <input
            id="video-upload"
            type="file"
            accept="video/*"
            onChange={handleFileChange}
            disabled={loading}
            className="file-input"
          />
          <div className="drop-hint">
            {isDragging ? (
              <p>Drop your video file here</p>
            ) : (
              <>
                <p>Drag and drop your video file here</p>
                <p className="or-text">or</p>
                <p className="click-text">Click to browse</p>
              </>
            )}
          </div>
        </div>

        {validationError && (
          <div className="validation-error" role="alert" aria-live="polite">
            {validationError}
          </div>
        )}

        {file && (
          <div className="file-info">
            <span>✓ {file.name}</span>
            <span className="file-size">
              ({(file.size / 1024 / 1024).toFixed(1)} MB)
            </span>
          </div>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="jump-type">Jump Type</label>
        <select
          id="jump-type"
          value={jumpType}
          onChange={(e) => onJumpTypeChange(e.target.value as 'cmj' | 'dropjump')}
          disabled={loading}
        >
          <option value="cmj">Counter Movement Jump (CMJ)</option>
          <option value="dropjump">Drop Jump</option>
        </select>
      </div>

      <div className="form-group checkbox-group">
        <label htmlFor="enable-debug" className="checkbox-label">
          <input
            id="enable-debug"
            type="checkbox"
            checked={enableDebug}
            onChange={(e) => onEnableDebugChange(e.target.checked)}
            disabled={loading}
            className="checkbox-input"
          />
          <span>Enable debug video overlay</span>
        </label>
        <p className="checkbox-hint">
          {enableDebug
            ? 'Debug video will be generated and available for download (~4-5 min slower)'
            : 'Results only (faster analysis ~20 seconds)'}
        </p>
      </div>

      <button
        className="analyze-button"
        onClick={onAnalyze}
        disabled={!file || loading}
      >
        {loading ? 'Analyzing...' : 'Analyze Video'}
      </button>

      <RecentUploads
        uploads={recentUploads}
        onSelect={handleSelectRecentUpload}
        onClear={onClearHistory || (() => {})}
      />

      <div className="info-text">
        <p>Supported formats: MP4, MOV, AVI</p>
        <p>Max file size: 500MB</p>
        <p>Analysis typically takes 10-60 seconds</p>
      </div>
    </div>
  )
}

export default UploadForm
