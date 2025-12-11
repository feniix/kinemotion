import { AnalysisResponse, METRIC_METADATA } from '../types/api'

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

  // Determine Jump Type context based on available metrics
  const isDropJump = 'ground_contact_time_ms' in metricsData || 'reactive_strength_index' in metricsData

  // --- Render Logic ---

  const renderScoreboard = () => {
    if (isDropJump) {
      const rsi = getMetric(['reactive_strength_index'], false, 'RSI')
      const height = getMetric(['jump_height_m', 'jump_height'], true, 'Height')
      const gct = getMetric(['ground_contact_time_ms', 'ground_contact_time'], false, 'Contact Time')

      return (
        <div className="kpi-grid">
          {renderMetricCard(rsi, { highlight: true, large: true })}
          {renderMetricCard(height)}
          {renderMetricCard(gct)}
        </div>
      )
    } else {
      // CMJ
      const height = getMetric(['jump_height_m', 'jump_height'], true, 'Jump Height')
      const velocity = getMetric(['peak_concentric_velocity_m_s', 'takeoff_velocity_mps'], false, 'Peak Velocity')
      const power = getMetric(['peak_power_w', 'peak_power'], false, 'Peak Power')

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
      getMetric(['countermovement_depth_m', 'countermovement_depth'], true, 'Depth'),
      getMetric(['eccentric_duration_ms', 'eccentric_duration'], false, 'Duration'),
      getMetric(['peak_eccentric_velocity_m_s'], false, 'Peak Vel'),
    ]

    // Phase 2: Explosion / Propulsion (Concentric)
    const explosionMetrics = [
      getMetric(['peak_concentric_velocity_m_s', 'takeoff_velocity_mps'], false, 'Peak Vel'),
      getMetric(['concentric_duration_ms', 'concentric_duration'], false, 'Duration'),
      getMetric(['peak_force_n'], false, 'Peak Force'),
    ]

    // Phase 3: Outcome (Flight & Landing)
    const outcomeMetrics = [
      getMetric(['flight_time_ms', 'flight_time'], false, 'Air Time'),
      getMetric(['jump_height_m', 'jump_height'], true, 'Height'),
      getMetric(['landing_force_normalized'], false, 'Landing Impact'),
    ]

    return (
      <div className="jump-timeline">
        <PhaseCard key="loading-phase" title="Loading (Eccentric)" metrics={loadingMetrics} />
        <div className="arrow">→</div>
        <PhaseCard key="explosion-phase" title="Explosion (Concentric)" metrics={explosionMetrics} />
        <div className="arrow">→</div>
        <PhaseCard key="outcome-phase" title="Outcome (Flight)" metrics={outcomeMetrics} />
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
        <h2>Analysis Results</h2>
        <div className="results-meta">
          {metrics.processing_time_s && (
            <span className="meta-tag">Processed in {metrics.processing_time_s.toFixed(1)}s</span>
          )}
          {metricsData['tracking_method'] && (
             <span className="meta-tag">Method: {String(metricsData['tracking_method'])}</span>
          )}
        </div>
      </div>

      {validationStatus && (
        <div className={`validation-banner ${validationStatus.toLowerCase()}`}>
          <div className="validation-header">
            <span className="status-icon">{validationStatus === 'PASS' ? '✓' : '⚠️'}</span>
            <strong>Quality Check: {validationStatus}</strong>
          </div>
          {hasErrors && (
             <p>Issues detected that may affect accuracy.</p>
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
        <h3 className="section-title">Key Performance Indicators</h3>
        {renderScoreboard()}
      </div>

      {/* 2. The Phase Timeline */}
      <div className="metrics-dashboard">
        <h3 className="section-title">Jump Phase Analysis</h3>
        {renderTimeline()}
      </div>

      {/* 3. Video Previews (Split view if debug video exists) */}
      <div className="metrics-dashboard" style={{ display: 'grid', gridTemplateColumns: metrics.debug_video_url ? '1fr 1fr' : '1fr', gap: '2rem' }}>
        {videoFile && (
          <div className="video-preview-container">
            <video
              src={URL.createObjectURL(videoFile)}
              controls
              className="analysis-video-player"
              playsInline
              title="Original Video"
            />
          </div>
        )}

        {metrics.debug_video_url && (
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

      {metrics.debug_video_url && (
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
           <a
              href={metrics.debug_video_url}
              download={`analysis_${new Date().toISOString()}.mp4`}
              className="download-link"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: 'var(--primary-color)', fontWeight: 500 }}
            >
              Download Analysis Video
            </a>
        </div>
      )}

      {/* 4. Detailed Breakdown */}
      <div className="metrics-dashboard">
        <h3 className="section-title">Additional Metrics</h3>
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
            Download Full JSON Report
          </a>
        </div>
      )}
    </div>
  )
}

export default ResultsDisplay
