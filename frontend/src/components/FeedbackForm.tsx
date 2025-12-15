import { useState } from 'react'
import { AnalysisResponse } from '../types/api'
import { useLanguage } from '../hooks/useLanguage'

interface FeedbackFormProps {
  analysisResponse: AnalysisResponse
  onSubmit: (feedback: FeedbackData) => void
  onCancel: () => void
}

interface FeedbackData {
  notes: string
  rating: number | null
  tags: string[]
}

export default function FeedbackForm({ analysisResponse, onSubmit, onCancel }: FeedbackFormProps) {
  const { t } = useLanguage()
  const COMMON_TAGS = t('feedback.commonTags', { returnObjects: true }) as string[]
  const [feedback, setFeedback] = useState<FeedbackData>({
    notes: '',
    rating: null,
    tags: []
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [customTag, setCustomTag] = useState('')

  const jumpType = analysisResponse.metrics?.data &&
    ('ground_contact_time_ms' in analysisResponse.metrics.data ||
     'reactive_strength_index' in analysisResponse.metrics.data)
    ? 'Drop Jump' : 'CMJ'

  const handleRatingClick = (rating: number) => {
    setFeedback(prev => ({ ...prev, rating: prev.rating === rating ? null : rating }))
  }

  const handleTagToggle = (tag: string) => {
    setFeedback(prev => ({
      ...prev,
      tags: prev.tags.includes(tag)
        ? prev.tags.filter(t => t !== tag)
        : [...prev.tags, tag]
    }))
  }

  const handleAddCustomTag = () => {
    if (customTag.trim() && !feedback.tags.includes(customTag.trim())) {
      setFeedback(prev => ({
        ...prev,
        tags: [...prev.tags, customTag.trim()]
      }))
      setCustomTag('')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      await onSubmit(feedback)
    } finally {
      setIsSubmitting(false)
    }
  }

  const isValid = feedback.notes.trim().length > 0 || feedback.rating !== null || feedback.tags.length > 0

  return (
    <div className="feedback-form-container">
      <div className="feedback-form">
        <div className="feedback-header">
          <h3>{t('feedback.heading', { jumpType })}</h3>
          <p>{t('feedback.subtitle')}</p>
        </div>

        <form onSubmit={handleSubmit} className="feedback-form-content">
          {/* Rating */}
          <div className="form-section">
            <label className="form-label">{t('feedback.overallRating')}</label>
            <div className="rating-container">
              {[1, 2, 3, 4, 5].map(star => (
                <button
                  key={star}
                  type="button"
                  className={`star-button ${feedback.rating === star ? 'selected' : ''}`}
                  onClick={() => handleRatingClick(star)}
                >
                  ★
                </button>
              ))}
              {feedback.rating && (
                <span className="rating-text">
                  {feedback.rating === 5 ? t('feedback.ratingLabels.excellent') :
                   feedback.rating === 4 ? t('feedback.ratingLabels.good') :
                   feedback.rating === 3 ? t('feedback.ratingLabels.average') :
                   feedback.rating === 2 ? t('feedback.ratingLabels.needsWork') : t('feedback.ratingLabels.poor')}
                </span>
              )}
            </div>
          </div>

          {/* Tags */}
          <div className="form-section">
            <label className="form-label">{t('feedback.tags')}</label>
            <div className="tags-container">
              <div className="common-tags">
                {COMMON_TAGS.map(tag => (
                  <button
                    key={tag}
                    type="button"
                    className={`tag-button ${feedback.tags.includes(tag) ? 'selected' : ''}`}
                    onClick={() => handleTagToggle(tag)}
                  >
                    {tag}
                  </button>
                ))}
              </div>

              <div className="custom-tag-input">
                <input
                  type="text"
                  value={customTag}
                  onChange={(e) => setCustomTag(e.target.value)}
                  placeholder={t('feedback.addCustomTag')}
                  className="tag-input"
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddCustomTag())}
                />
                <button
                  type="button"
                  onClick={handleAddCustomTag}
                  className="add-tag-button"
                  disabled={!customTag.trim()}
                >
                  {t('feedback.addButton')}
                </button>
              </div>

              {feedback.tags.length > 0 && (
                <div className="selected-tags">
                  {feedback.tags.map(tag => (
                    <span key={tag} className="selected-tag">
                      {tag}
                      <button
                        type="button"
                        onClick={() => handleTagToggle(tag)}
                        className="remove-tag"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Notes */}
          <div className="form-section">
            <label className="form-label" htmlFor="feedback-notes">
              {t('feedback.coachNotes')}
            </label>
            <textarea
              id="feedback-notes"
              value={feedback.notes}
              onChange={(e) => setFeedback(prev => ({ ...prev, notes: e.target.value }))}
              placeholder="Provide detailed feedback on technique, areas for improvement, strengths, observations..."
              className="notes-textarea"
              rows={6}
            />
            <div className="notes-help">
              {t('feedback.notesHelp')}
            </div>
          </div>

          {/* Actions */}
          <div className="form-actions">
            <button
              type="button"
              onClick={onCancel}
              className="cancel-button"
              disabled={isSubmitting}
            >
              {t('feedback.cancel')}
            </button>
            <button
              type="submit"
              className="submit-button"
              disabled={!isValid || isSubmitting}
            >
              {isSubmitting ? t('feedback.saving') : t('feedback.saveFeedback')}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
