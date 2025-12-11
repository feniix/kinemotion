import { useState, useRef } from 'react'
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
  const fileInputRef = useRef<HTMLInputElement>(null); // Create a ref for the file input

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
    <div className="upload-controller">
      {/* 1. Context Configuration Bar */}
      <div className="config-bar">
        <div className="jump-selector">
          <button
            className={`type-btn ${jumpType === 'cmj' ? 'active' : ''}`}
            onClick={() => onJumpTypeChange('cmj')}
            title="Counter Movement Jump"
          >
            CMJ
          </button>
          <button
            className={`type-btn ${jumpType === 'dropjump' ? 'active' : ''}`}
            onClick={() => onJumpTypeChange('dropjump')}
            title="Drop Jump"
          >
            Drop Jump
          </button>
        </div>

        <label className="debug-toggle">
          <input
            type="checkbox"
            checked={enableDebug}
            onChange={(e) => onEnableDebugChange(e.target.checked)}
          />
          <span className="toggle-label">Generate Overlay</span>
        </label>
      </div>

      {/* 2. Unified Action Zone */}
      <div className={`drop-zone-container ${file ? 'has-file' : ''}`}>
        <div
          className={`upload-drop-zone ${isDragging ? 'dragging' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <input
            type="file"
            accept="video/*"
            onChange={handleFileChange}
            className="file-input"
            disabled={loading}
            data-testid="file-input"
            ref={fileInputRef} // Assign the ref to the input
          />

          {!file ? (
            <div className="empty-state">
              <div className="upload-icon">⏏</div>
              <p>Drag analysis video here</p>
              <span className="sub-text">or click to browse (max 500MB)</span>
            </div>
          ) : (
            <div className="file-ready-state">
              <div className="file-preview-icon">🎬</div>
              <div className="file-details">
                <span className="filename">{file.name}</span>
                <span className="filesize">{(file.size / 1024 / 1024).toFixed(1)} MB</span>
              </div>
              <button className="change-file-btn" onClick={() => {
                onFileChange(null);
                if (fileInputRef.current) fileInputRef.current.value = ''; // Reset file input using ref
              }}>Change</button>
            </div>
          )}
        </div>

        {validationError && (
          <div className="validation-error" role="alert" aria-live="polite">
            {validationError}
          </div>
        )}

        {/* 3. Primary Action attached to the file */}
        <button
          className="analyze-hero-button"
          onClick={onAnalyze}
          disabled={!file || loading}
        >
          {loading ? (
            <span className="loading-pulse">Analyzing...</span>
          ) : (
            <>Run Analysis <span className="arrow">→</span></>
          )}
        </button>
      </div>

      <RecentUploads
        uploads={recentUploads}
        onSelect={handleSelectRecentUpload}
        onClear={onClearHistory || (() => {})}
      />
    </div>
  )
}

export default UploadForm
