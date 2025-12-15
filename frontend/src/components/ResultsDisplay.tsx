import { AnalysisResponse, METRIC_METADATA } from '../types/api'
import { useEffect, useState } from 'react'
import FeedbackForm from './FeedbackForm'
import FeatureRequestButton from './FeatureRequestButton'
import { useDatabaseStatus } from '../hooks/useDatabaseStatus'
import { useLanguage } from '../hooks/useLanguage'
import { useAuth } from '../hooks/useAuth'
import { EXTERNAL_LINKS } from '../config/links'
import './FeedbackForm.css'

interface ResultsDisplayProps {
  metrics: AnalysisResponse
  videoFile?: File | null
}

interface MetricCardProps {
  label: string
  value: string | number
  unit: string
  description?: string
  trend?: 'neutral' | 'positive' | 'negative'
  highlight?: boolean
  large?: boolean
}

interface FormattedMetric extends MetricCardProps {
  key: string
}

function MetricCard({ label, value, unit, description, highlight = false, large = false }: MetricCardProps) {
  return (
    <div className={`metric-card ${highlight ? 'highlight' : ''}`} title={description}>
      <div className="metric-card-header">
        <span className="metric-card-label">{label}</span>
        {description && <span className="info-icon" title={description}>ⓘ</span>}
      </div>
      <div className="metric-card-value">
        <span className={`value-text ${large ? 'large' : ''}`}>{value}</span>
        <span className="value-unit">{unit}</span>
      </div>
    </div>
  )
}

interface PhaseCardProps {
  title: string
  metrics: Array<FormattedMetric | null>
}

function PhaseCard({ title, metrics }: PhaseCardProps) {
  const validMetrics = metrics.filter((m): m is FormattedMetric => m !== null)

  if (validMetrics.length === 0) return null

  return (
    <div className="phase-card">
      <div className="phase-header">
        <span>{title}</span>
      </div>
      <div className="phase-metrics">
        {validMetrics.map((m) => {
          const { key, ...props } = m
          return (
            <div key={key} className="metric-compact" title={props.description}>
              <span className="label">{props.label}</span>
              <div>
                <span className="value">{props.value}</span>
                <span className="unit">{props.unit}</span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function ResultsDisplay({ metrics, videoFile }: ResultsDisplayProps) {
  const [localOriginalUrl, setLocalOriginalUrl] = useState<string | null>(null)
  const [showFeedbackForm, setShowFeedbackForm] = useState(false)
  const { status: dbStatus, loading: dbLoading } = useDatabaseStatus()
  const { t } = useLanguage()

  useEffect(() => {
    if (!videoFile) {
      setLocalOriginalUrl(null)
      return
    }

    const url = URL.createObjectURL(videoFile)
    setLocalOriginalUrl(url)

    return () => {
      URL.revokeObjectURL(url)
    }
  }, [videoFile])

  const originalSrc = metrics.original_video_url || localOriginalUrl || undefined
  const showOriginal = Boolean(originalSrc)
  const showDebug = Boolean(metrics.debug_video_url)
  // Extract data
  const metricsData = metrics.metrics?.data || {}
  const validationStatus = metrics.metrics?.validation?.status
  const validationIssues = metrics.metrics?.validation?.issues ?? []
  const hasErrors = validationIssues.some(issue => issue.severity === 'ERROR')

  // Helper to safely get and format a metric
  const getMetric = (keyPatterns: string[], asCm = false, labelOverride?: string): FormattedMetric | null => {
    // Find the first matching key in the data
    const key = keyPatterns.find(k => k in metricsData)
    if (!key) return null

    let value = metricsData[key]
    if (typeof value !== 'number') return null

    // Convert meters to cm if requested
    if (asCm && (key.endsWith('_m') || key === 'jump_height' || key === 'countermovement_depth')) {
      value = value * 100
    }

    const metadata = METRIC_METADATA[key] || {}

    // Format number
    let formattedValue: string
    if (Math.abs(value) < 0.01 && value !== 0) {
      formattedValue = value.toExponential(2)
    } else {
      formattedValue = value.toFixed(2)
    }

    return {
      key,
      label: labelOverride || key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '), // Simple fallback label
      value: formattedValue,
      unit: asCm ? 'cm' : (metadata.unit || ''),
      description: metadata.description || ''
    }
  }

  const renderMetricCard = (metric: FormattedMetric | null, props: Partial<MetricCardProps> = {}) => {
    if (!metric) return null
    const { key, ...rest } = metric
    return <MetricCard key={key} {...rest} {...props} />
  }

  const { session } = useAuth()

  const handleFeedbackSubmit = async (feedback: { notes: string; rating: number | null; tags: string[] }) => {
    try {
      const token = session?.access_token
      console.log('[Feedback] Session:', session)
      console.log('[Feedback] Token:', token)

      if (!token) {
        console.error('[Feedback] No token available. Session:', session)
        alert('Please log in to save feedback')
        return
      }

      // Get backend URL from environment
      const backendUrl = import.meta.env.VITE_API_URL || window.location.origin

      // For now, we'll create a session first, then add feedback
      // In a real implementation, the session ID should be returned from the analyze endpoint
      const sessionData = {
        jump_type: isDropJump ? 'drop_jump' : 'cmj',
        quality_preset: 'balanced', // This could be made configurable
        analysis_data: metrics.metrics,
        original_video_url: metrics.original_video_url,
        debug_video_url: metrics.debug_video_url,
        results_json_url: metrics.results_url,
        processing_time_s: metrics.processing_time_s,
      }

      // First create the analysis session
      const sessionResponse = await fetch(`${backendUrl}/api/analysis/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(sessionData)
      })

      if (!sessionResponse.ok) {
        throw new Error('Failed to create analysis session')
      }

      const sessionResult: { id: string } = await sessionResponse.json()
      const sessionId = sessionResult.id

      // Then add the feedback
      const feedbackData = {
        notes: feedback.notes,
        rating: feedback.rating,
        tags: feedback.tags
      }

      const feedbackResponse = await fetch(`${backendUrl}/api/analysis/sessions/${sessionId}/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(feedbackData)
      })

      if (!feedbackResponse.ok) {
        throw new Error('Failed to save feedback')
      }

      setShowFeedbackForm(false)
      // Show success message
      alert('Feedback saved successfully!')
    } catch (error) {
      console.error('Error saving feedback:', error)
      alert('Failed to save feedback. Please try again.')
    }
  }

  // Determine Jump Type context based on available metrics
  const isDropJump = 'ground_contact_time_ms' in metricsData || 'reactive_strength_index' in metricsData

  // --- Render Logic ---

  const renderScoreboard = () => {
    if (isDropJump) {
      const rsi = getMetric(['reactive_strength_index'], false, t('results.metrics.rsi'))
      const height = getMetric(['jump_height_m', 'jump_height'], true, t('results.metrics.height'))
      const gct = getMetric(['ground_contact_time_ms', 'ground_contact_time'], false, t('results.metrics.contactTime'))

      return (
        <div className="kpi-grid">
          {renderMetricCard(rsi, { highlight: true, large: true })}
          {renderMetricCard(height)}
          {renderMetricCard(gct)}
        </div>
      )
    } else {
      // CMJ
      const height = getMetric(['jump_height_m', 'jump_height'], true, t('results.metrics.jumpHeight'))
      const velocity = getMetric(['peak_concentric_velocity_m_s', 'takeoff_velocity_mps'], false, t('results.metrics.peakVelocity'))
      const power = getMetric(['peak_power_w', 'peak_power'], false, t('results.metrics.peakPower'))

      return (
        <div className="kpi-grid">
          {renderMetricCard(height, { highlight: true, large: true })}
          {renderMetricCard(velocity)}
          {renderMetricCard(power)}
        </div>
      )
    }
  }

  const renderTimeline = () => {
    // Phase 1: Preparation / Loading (Eccentric)
    const loadingMetrics = [
      getMetric(['countermovement_depth_m', 'countermovement_depth'], true, t('results.metrics.depth')),
      getMetric(['eccentric_duration_ms', 'eccentric_duration'], false, t('results.metrics.duration')),
      getMetric(['peak_eccentric_velocity_m_s'], false, t('results.metrics.peakVel')),
    ]

    // Phase 2: Explosion / Propulsion (Concentric)
    const explosionMetrics = [
      getMetric(['peak_concentric_velocity_m_s', 'takeoff_velocity_mps'], false, t('results.metrics.peakVel')),
      getMetric(['concentric_duration_ms', 'concentric_duration'], false, t('results.metrics.duration')),
      getMetric(['peak_force_n'], false, 'Peak Force'),
    ]

    // Phase 3: Outcome (Flight & Landing)
    const outcomeMetrics = [
      getMetric(['flight_time_ms', 'flight_time'], false, t('results.metrics.airTime')),
      getMetric(['jump_height_m', 'jump_height'], true, t('results.metrics.height')),
      getMetric(['landing_force_normalized'], false, t('results.metrics.landingImpact')),
    ]

    return (
      <div className="jump-timeline">
        <PhaseCard key="loading-phase" title={t('results.phases.loading')} metrics={loadingMetrics} />
        <div className="arrow">→</div>
        <PhaseCard key="explosion-phase" title={t('results.phases.explosion')} metrics={explosionMetrics} />
        <div className="arrow">→</div>
        <PhaseCard key="outcome-phase" title={t('results.phases.outcome')} metrics={outcomeMetrics} />
      </div>
    )
  }

  // Render secondary metrics in a grid (everything else)
  const renderDetails = () => {
    const excludeKeys = new Set([
      'reactive_strength_index', 'jump_height', 'jump_height_m', 'jump_height_cm',
      'ground_contact_time', 'ground_contact_time_ms',
      'flight_time', 'flight_time_ms', 'flight_time_s',
      'peak_concentric_velocity_m_s', 'takeoff_velocity_mps',
      'countermovement_depth_m', 'countermovement_depth', 'countermovement_depth_cm',
      'eccentric_duration_ms', 'concentric_duration_ms',
      'tracking_method', 'peak_eccentric_velocity_m_s', 'landing_force_normalized',
      'peak_force_n'
    ])

    return Object.entries(metricsData)
      .filter(([key, val]) => !excludeKeys.has(key) && typeof val === 'number' && !key.includes('frame'))
      .map(([key, value]) => {
        const metadata = METRIC_METADATA[key] || {}
        const formatLabel = (k: string) => k.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')

        return (
          <div key={key} className="detail-item">
            <span className="detail-label">
              {formatLabel(key)}
              {metadata.description && <span className="info-icon small" title={metadata.description}>ⓘ</span>}
            </span>
            <span className="detail-value">
              {typeof value === 'number' ? value.toFixed(2) : value} {metadata.unit}
            </span>
          </div>
        )
      })
  }

  return (
    <div className="results-container animate-fade-in">
      <div className="results-header">
        <h2>{t('results.heading')}</h2>
        <div className="results-meta">
          {metrics.processing_time_s && (
            <span className="meta-tag">{t('results.processedTime', { time: metrics.processing_time_s.toFixed(1) })}</span>
          )}
          {metricsData['tracking_method'] && (
             <span className="meta-tag">{t('results.method', { type: String(metricsData['tracking_method']) })}</span>
          )}
        </div>
      </div>

      {validationStatus && (
        <div className={`validation-banner ${validationStatus.toLowerCase()}`}>
          <div className="validation-header">
            <span className="status-icon">
              {validationStatus === 'PASS' ? '✓' : validationStatus === 'PASS_WITH_WARNINGS' ? 'ℹ' : '⚠️'}
            </span>
            <strong>{t('results.validationStatus', { status: validationStatus.replace(/_/g, ' ') })}</strong>
          </div>
          {hasErrors && (
             <p>{t('results.issuesDetected')}</p>
          )}
          {validationIssues.length > 0 && (
            <ul className="validation-list">
              {validationIssues.map((issue, idx) => (
                <li key={idx} className={`issue-${issue.severity.toLowerCase()}`}>
                  {issue.message}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* 1. The Scoreboard (Hero Metrics) */}
      <div className="metrics-dashboard">
        <h3 className="section-title">{t('results.kpiSection')}</h3>
        {renderScoreboard()}
      </div>

      {/* 2. The Phase Timeline */}
      <div className="metrics-dashboard">
        <h3 className="section-title">{t('results.phaseSection')}</h3>
        {renderTimeline()}
      </div>

      {/* 3. Video Previews (Split view if debug video exists) */}
      <div className="metrics-dashboard" style={{ display: 'grid', gridTemplateColumns: (showOriginal && showDebug) ? '1fr 1fr' : '1fr', gap: '2rem' }}>
        {showOriginal && (
          <div className="video-preview-container">
            <video
              src={originalSrc}
              controls
              className="analysis-video-player"
              playsInline
              title="Original Video"
            />
          </div>
        )}

        {showDebug && (
          <div className="video-preview-container debug-video">
            <video
              src={metrics.debug_video_url}
              controls
              className="analysis-video-player"
              playsInline
              title="Analysis Overlay"
            />
          </div>
        )}
      </div>

      {(showOriginal || showDebug) && (
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          {showOriginal && (
            <a
              href={originalSrc}
              download={`original_${new Date().toISOString()}.mp4`}
              className="download-link"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: 'var(--primary-color)', fontWeight: 500, marginRight: showDebug ? '1rem' : undefined }}
            >
              {t('results.downloadOriginal')}
            </a>
          )}

          {showDebug && (
            <a
              href={metrics.debug_video_url}
              download={`analysis_${new Date().toISOString()}.mp4`}
              className="download-link"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: 'var(--primary-color)', fontWeight: 500 }}
            >
              {t('results.downloadAnalysis')}
            </a>
          )}
        </div>
      )}

      {/* 4. Detailed Breakdown */}
      <div className="metrics-dashboard">
        <h3 className="section-title">{t('results.detailsSection')}</h3>
        <div className="details-grid">
          {renderDetails()}
        </div>
      </div>

      {metrics.results_url && (
        <div className="actions-bar">
          <a
            href={metrics.results_url}
            download
            className="download-button primary"
            target="_blank"
            rel="noopener noreferrer"
          >
            {t('results.downloadFullReport')}
          </a>
        </div>
      )}

      {/* Feedback & Feature Request Section */}
      <div className="metrics-dashboard" style={{
        background: '#f8fafc',
        border: '1px solid #e2e8f0',
        borderRadius: '8px',
        padding: '1rem',
        margin: '1rem 0'
      }}>
        <div style={{ color: '#475569', fontWeight: '500', marginBottom: '1rem' }}>
          {t('results.feedback.heading')}
        </div>

        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
          {/* Database-dependent feedback */}
          {dbStatus?.database_connected ? (
            <button
              onClick={() => setShowFeedbackForm(true)}
              className="feedback-button"
              style={{
                background: '#10b981',
                border: 'none',
                borderRadius: '6px',
                padding: '0.75rem 1.5rem',
                color: 'white',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'background-color 0.2s'
              }}
              onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#059669'}
              onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#10b981'}
            >
              {t('results.feedback.coachFeedback')}
            </button>
          ) : (
            <span style={{
              color: '#6b7280',
              fontSize: '0.875rem',
              fontStyle: 'italic'
            }}>
              {t('results.feedback.feedbackUnavailable')}
            </span>
          )}

          {/* Feature request - always available */}
          <FeatureRequestButton variant="primary" showIcon={true} />

          {/* General feedback */}
          <a
            href={EXTERNAL_LINKS.GITHUB_ISSUES}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              background: 'transparent',
              border: '1px solid #6366f1',
              borderRadius: '6px',
              padding: '0.75rem 1.5rem',
              color: '#6366f1',
              fontSize: '0.875rem',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'all 0.2s',
              textDecoration: 'none',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.backgroundColor = '#6366f1'
              e.currentTarget.style.color = 'white'
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent'
              e.currentTarget.style.color = '#6366f1'
            }}
            title="Report an issue or request a feature on GitHub"
          >
            {t('results.feedback.reportIssue')}
          </a>
        </div>

        <div style={{ marginTop: '0.75rem', color: '#64748b', fontSize: '0.75rem' }}>
          {t('results.feedback.helpText')}
        </div>
      </div>

      {/* Show database status banner if there are issues */}
      {!dbLoading && !dbStatus?.database_connected && (
        <div className="metrics-dashboard" style={{
          background: '#fef2f2',
          border: '1px solid #fecaca',
          borderRadius: '8px',
          padding: '1rem',
          margin: '1rem 0'
        }}>
          <div style={{ color: '#dc2626', fontWeight: '500', marginBottom: '0.5rem' }}>
            {t('results.database.unavailable')}
          </div>
          <div style={{ color: '#7f1d1d', fontSize: '0.875rem' }}>
            {dbStatus?.message || t('results.database.defaultMessage')}
          </div>
        </div>
      )}

      {/* Feedback Form Modal */}
      {showFeedbackForm && (
        <FeedbackForm
          analysisResponse={metrics}
          onSubmit={handleFeedbackSubmit}
          onCancel={() => setShowFeedbackForm(false)}
        />
      )}
    </div>
  )
}

export default ResultsDisplay
