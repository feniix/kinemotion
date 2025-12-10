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
}

function MetricCard({ label, value, unit, description, highlight = false }: MetricCardProps) {
  return (
    <div className={`metric-card ${highlight ? 'highlight' : ''}`} title={description}>
      <div className="metric-card-header">
        <span className="metric-card-label">{label}</span>
        {description && <span className="info-icon" title={description}>ⓘ</span>}
      </div>
      <div className="metric-card-value">
        <span className="value-text">{value}</span>
        <span className="value-unit">{unit}</span>
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
  const getMetric = (keyPatterns: string[], asCm = false) => {
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
      value: formattedValue,
      unit: asCm ? 'cm' : (metadata.unit || ''),
      description: metadata.description || ''
    }
  }

  // Determine Jump Type context based on available metrics
  const isDropJump = 'ground_contact_time_ms' in metricsData || 'reactive_strength_index' in metricsData

  // Define Key Metrics based on jump type
  const renderKeyMetrics = () => {
    const cards = []

    if (isDropJump) {
      const rsi = getMetric(['reactive_strength_index'])
      if (rsi) cards.push(<MetricCard key="rsi" label="RSI" value={rsi.value} unit={rsi.unit} description={rsi.description} highlight />)

      const height = getMetric(['jump_height_m', 'jump_height'], true)
      if (height) cards.push(<MetricCard key="height" label="Jump Height" value={height.value} unit={height.unit} description={height.description} highlight />)

      const gct = getMetric(['ground_contact_time_ms', 'ground_contact_time'])
      if (gct) cards.push(<MetricCard key="gct" label="Ground Contact" value={gct.value} unit={gct.unit} description={gct.description} />)

      const ft = getMetric(['flight_time_ms', 'flight_time'])
      if (ft) cards.push(<MetricCard key="ft" label="Flight Time" value={ft.value} unit={ft.unit} description={ft.description} />)
    } else {
      // CMJ
      const height = getMetric(['jump_height_m', 'jump_height'], true)
      if (height) cards.push(<MetricCard key="height" label="Jump Height" value={height.value} unit={height.unit} description={height.description} highlight />)

      const velocity = getMetric(['peak_concentric_velocity_m_s', 'takeoff_velocity_mps'])
      if (velocity) cards.push(<MetricCard key="vel" label="Peak Velocity" value={velocity.value} unit={velocity.unit} description={velocity.description} />)

      const depth = getMetric(['countermovement_depth_m', 'countermovement_depth'], true)
      if (depth) cards.push(<MetricCard key="depth" label="Squat Depth" value={depth.value} unit={depth.unit} description={depth.description} />)

      const totalTime = getMetric(['total_movement_time_ms'])
      if (totalTime) cards.push(<MetricCard key="total" label="Total Time" value={totalTime.value} unit={totalTime.unit} description={totalTime.description} />)
    }

    return cards
  }

  // Render secondary metrics in a grid
  const renderDetails = () => {
    const excludeKeys = new Set([
      'reactive_strength_index', 'jump_height', 'jump_height_m',
      'ground_contact_time', 'ground_contact_time_ms',
      'flight_time', 'flight_time_ms',
      'peak_concentric_velocity_m_s', 'countermovement_depth_m', 'countermovement_depth',
      'tracking_method' // Hide metadata
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

      {videoFile && (
        <div className="video-preview-container">
          <h3 className="section-subtitle">Original Video</h3>
          <video
            src={URL.createObjectURL(videoFile)}
            controls
            className="analysis-video-player"
            playsInline
          />
        </div>
      )}

      {metrics.debug_video_url && (
        <div className="video-preview-container debug-video">
          <h3 className="section-subtitle">Analysis Overlay</h3>
          <video
            src={metrics.debug_video_url}
            controls
            className="analysis-video-player"
            playsInline
          />
          <div className="video-actions">
            <a
              href={metrics.debug_video_url}
              download={`analysis_${new Date().toISOString()}.mp4`}
              className="download-link"
              target="_blank"
              rel="noopener noreferrer"
            >
              Download Overlay Video
            </a>
          </div>
        </div>
      )}

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

      <div className="metrics-dashboard">
        <h3 className="section-title">Key Performance Indicators</h3>
        <div className="kpi-grid">
          {renderKeyMetrics()}
        </div>

        <h3 className="section-title">Detailed Breakdown</h3>
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
