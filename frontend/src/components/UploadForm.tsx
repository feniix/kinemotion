import { useState, useRef } from 'react'
import RecentUploads from './RecentUploads'
import { useLanguage } from '../hooks/useLanguage'
import { RecentUpload } from '../hooks/useRecentUploads'
import type { BiologicalSex, JumpType, TrainingLevel } from '../types/api'

interface UploadFormProps {
  file: File | null
  jumpType: JumpType
  loading: boolean
  enableDebug: boolean
  sex: BiologicalSex | null
  age: number | null
  trainingLevel: TrainingLevel | null
  recentUploads: RecentUpload[]
  onFileChange: (file: File | null) => void
  onJumpTypeChange: (jumpType: JumpType) => void
  onEnableDebugChange: (enable: boolean) => void
  onSexChange: (sex: BiologicalSex | null) => void
  onAgeChange: (age: number | null) => void
  onTrainingLevelChange: (level: TrainingLevel | null) => void
  onAnalyze: () => void
  onClearHistory: () => void
}

const MAX_FILE_SIZE = 500 * 1024 * 1024 // 500MB

function UploadForm({
  file,
  jumpType,
  loading,
  enableDebug,
  sex,
  age,
  trainingLevel,
  recentUploads,
  onFileChange,
  onJumpTypeChange,
  onEnableDebugChange,
  onSexChange,
  onAgeChange,
  onTrainingLevelChange,
  onAnalyze,
  onClearHistory,
}: UploadFormProps) {
  const [validationError, setValidationError] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [showAthleteProfile, setShowAthleteProfile] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null); // Create a ref for the file input
  const { t } = useLanguage()

  const validateFile = (selectedFile: File): boolean => {
    // Validate file size
    if (selectedFile.size > MAX_FILE_SIZE) {
      setValidationError(
        t('uploadForm.errors.fileTooLarge', { size: (selectedFile.size / 1024 / 1024).toFixed(1) })
      )
      return false
    }

    // Validate file type
    if (!selectedFile.type.startsWith('video/')) {
      setValidationError(t('uploadForm.errors.invalidFileType'))
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

  const handleSelectRecentUpload = (_filename: string, jumpType: JumpType) => {
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
            title={t('uploadForm.cmjTitle')}
          >
            {t('uploadForm.cmjLabel')}
          </button>
          <button
            className={`type-btn ${jumpType === 'dropjump' ? 'active' : ''}`}
            onClick={() => onJumpTypeChange('dropjump')}
            title={t('uploadForm.dropJumpTitle')}
          >
            {t('uploadForm.dropJumpLabel')}
          </button>
        </div>

        <label className="debug-toggle">
          <input
            type="checkbox"
            checked={enableDebug}
            onChange={(e) => onEnableDebugChange(e.target.checked)}
          />
          <span className="toggle-label">{t('uploadForm.debugToggle')}</span>
        </label>
      </div>

      {/* 2. Athlete Profile (Optional) */}
      <div className="athlete-profile-section">
        <button
          type="button"
          className="athlete-profile-toggle"
          onClick={() => setShowAthleteProfile(!showAthleteProfile)}
          aria-expanded={showAthleteProfile}
        >
          <span>{t('uploadForm.athleteProfile.title')}</span>
          <span className="toggle-arrow">{showAthleteProfile ? '▲' : '▼'}</span>
        </button>

        {showAthleteProfile && (
          <div className="athlete-profile-fields">
            <p className="athlete-profile-hint">{t('uploadForm.athleteProfile.hint')}</p>

            <div className="profile-field">
              <label className="profile-label">{t('uploadForm.athleteProfile.sex')}</label>
              <div className="sex-selector">
                <button
                  type="button"
                  className={`sex-btn ${sex === 'male' ? 'active' : ''}`}
                  onClick={() => onSexChange(sex === 'male' ? null : 'male')}
                >
                  {t('uploadForm.athleteProfile.male')}
                </button>
                <button
                  type="button"
                  className={`sex-btn ${sex === 'female' ? 'active' : ''}`}
                  onClick={() => onSexChange(sex === 'female' ? null : 'female')}
                >
                  {t('uploadForm.athleteProfile.female')}
                </button>
              </div>
            </div>

            <div className="profile-field">
              <label className="profile-label" htmlFor="athlete-age">{t('uploadForm.athleteProfile.age')}</label>
              <input
                id="athlete-age"
                type="number"
                min={5}
                max={120}
                placeholder={t('uploadForm.athleteProfile.agePlaceholder')}
                value={age ?? ''}
                onChange={(e) => {
                  const val = e.target.value
                  onAgeChange(val ? parseInt(val, 10) : null)
                }}
                className="age-input"
              />
            </div>

            <div className="profile-field">
              <label className="profile-label" htmlFor="training-level">{t('uploadForm.athleteProfile.trainingLevel')}</label>
              <select
                id="training-level"
                value={trainingLevel ?? ''}
                onChange={(e) => onTrainingLevelChange((e.target.value || null) as TrainingLevel | null)}
                className="training-select"
              >
                <option value="">{t('uploadForm.athleteProfile.notSpecified')}</option>
                <option value="untrained">{t('uploadForm.athleteProfile.levels.untrained')}</option>
                <option value="recreational">{t('uploadForm.athleteProfile.levels.recreational')}</option>
                <option value="trained">{t('uploadForm.athleteProfile.levels.trained')}</option>
                <option value="competitive">{t('uploadForm.athleteProfile.levels.competitive')}</option>
                <option value="elite">{t('uploadForm.athleteProfile.levels.elite')}</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {/* 3. Unified Action Zone */}
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
              <p>{t('uploadForm.uploadPrompt')}</p>
              <span className="sub-text">{t('uploadForm.uploadSubtext')}</span>
            </div>
          ) : (
            <div className="file-ready-state">
              <div className="file-preview-icon">🎬</div>
              <div className="file-details">
                <span className="filename">{t('uploadForm.fileName', { name: file.name })}</span>
                <span className="filesize">{t('uploadForm.fileSize', { size: (file.size / 1024 / 1024).toFixed(1) })}</span>
              </div>
              <button className="change-file-btn" onClick={() => {
                onFileChange(null);
                if (fileInputRef.current) fileInputRef.current.value = ''; // Reset file input using ref
              }}>{t('uploadForm.changeFile')}</button>
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
            <span className="loading-pulse">{t('uploadForm.analyzing')}</span>
          ) : (
            <>{t('uploadForm.analyzeButton')} <span className="arrow">→</span></>
          )}
        </button>
      </div>

      <RecentUploads
        uploads={recentUploads}
        onSelect={handleSelectRecentUpload}
        onClear={onClearHistory}
      />
    </div>
  )
}

export default UploadForm
