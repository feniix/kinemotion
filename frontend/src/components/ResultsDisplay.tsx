import { AnalysisResponse, METRIC_METADATA } from '../types/api'

interface ResultsDisplayProps {
  metrics: AnalysisResponse
}

function ResultsDisplay({ metrics }: ResultsDisplayProps) {
  const formatValue = (value: string | number): string => {
    if (typeof value === 'number') {
      // For zero, return "0.00"
      if (value === 0) {
        return '0.00'
      }
      // Handle very small numbers (less than 0.001)
      if (Math.abs(value) < 0.001) {
        return value.toExponential(3)
      }
      // Round to 2 decimal places for normal values
      return value.toFixed(2)
    }
    return String(value)
  }

  const formatLabel = (key: string): string => {
    // Convert snake_case to Title Case
    return key
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  const getMetricUnit = (key: string): string => {
    return METRIC_METADATA[key]?.unit || ''
  }

  const getMetricDescription = (key: string): string => {
    return METRIC_METADATA[key]?.description || ''
  }

  // Extract actual metrics from nested structure
  const metricsData = metrics.metrics?.data || {}
  const hasMetrics = Object.keys(metricsData).length > 0

  // Check for validation issues
  const validationStatus = metrics.metrics?.validation?.status
  const validationIssues = metrics.metrics?.validation?.issues || []
  const hasErrors = validationIssues.some((issue: any) => issue.severity === 'ERROR')

  return (
    <div className="results-display" role="region" aria-live="polite" aria-label="Analysis results">
      <h2>Analysis Results</h2>

      <p>{metrics.message}</p>

      {metrics.processing_time_s && (
        <div className="analysis-time">
          Analysis completed in {metrics.processing_time_s.toFixed(1)} seconds
        </div>
      )}

      {validationStatus && (
        <div className={`validation-status ${validationStatus.toLowerCase()}`} role="alert">
          <strong>Analysis Status: {validationStatus}</strong>
          {hasErrors && (
            <p className="status-warning">
              ⚠️ Issues detected with this video analysis. The results below may not be reliable.
            </p>
          )}
        </div>
      )}

      {validationIssues.length > 0 && (
        <div className="validation-issues">
          <h3>Validation Issues</h3>
          <ul>
            {validationIssues.map((issue: any, idx: number) => (
              <li key={idx} className={`issue-${issue.severity.toLowerCase()}`}>
                <strong>[{issue.severity}]</strong> {issue.metric}: {issue.message}
              </li>
            ))}
          </ul>
        </div>
      )}

      {hasMetrics && (
        <div className="metrics-table">
          <table>
            <thead>
              <tr>
                <th>Metric</th>
                <th>Value</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(metricsData).map(([key, value]) => {
                // Skip null, undefined, or NaN values
                if (value === null || value === undefined) {
                  return null
                }

                // For numbers, skip NaN
                if (typeof value === 'number' && Number.isNaN(value)) {
                  return null
                }

                // Skip non-numeric/non-string types
                if (typeof value !== 'number' && typeof value !== 'string') {
                  return null
                }

                // Skip frame numbers and tracking method (metadata, not metrics)
                if (key.includes('frame') || key === 'tracking_method') {
                  return null
                }

                const unit = getMetricUnit(key)
                const description = getMetricDescription(key)

                return (
                  <tr
                    key={key}
                    className={description ? 'metric-with-tooltip' : ''}
                    aria-label={`${formatLabel(key)}: ${formatValue(value)} ${unit}`.trim()}
                  >
                    <td className="metric-label">
                      <span className="metric-name">{formatLabel(key)}</span>
                      {description && (
                        <span className="metric-info">
                          <span className="info-icon" title={description}>
                            ⓘ
                          </span>
                          <span className="metric-tooltip">{description}</span>
                        </span>
                      )}
                    </td>
                    <td className="metric-value">
                      <span className="value-amount">{formatValue(value)}</span>
                      {unit && <span className="value-unit">{unit}</span>}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {metrics.results_url && (
        <div className="download-section">
          <a
            href={metrics.results_url}
            download
            className="download-button"
            target="_blank"
            rel="noopener noreferrer"
          >
            Download Detailed Results
          </a>
        </div>
      )}
    </div>
  )
}

export default ResultsDisplay
