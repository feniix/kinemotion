import type { MetricInterpretation } from '../types/api'
import { useLanguage } from '../hooks/useLanguage'

interface BenchmarkIndicatorProps {
  interpretation: MetricInterpretation
}

const CATEGORY_COLORS: Record<string, string> = {
  poor: '#ef4444',
  below_average: '#f97316',
  average: '#eab308',
  above_average: '#22c55e',
  good: '#22c55e',
  very_good: '#10b981',
  excellent: '#06b6d4',
  // Countermovement depth special categories
  too_shallow: '#f97316',
  optimal: '#10b981',
  deep: '#eab308',
  too_deep: '#ef4444',
}

function BenchmarkIndicator({ interpretation }: BenchmarkIndicatorProps) {
  const { t } = useLanguage()
  const color = CATEGORY_COLORS[interpretation.category] || '#94a3b8'
  const categoryLabel = t(`results.categories.${interpretation.category}`)

  return (
    <div className="benchmark-indicator">
      <div className="benchmark-category" style={{ color }}>
        <span className="benchmark-dot" style={{ backgroundColor: color }} />
        {categoryLabel}
      </div>
      <div className="benchmark-range">
        {interpretation.range.low}&ndash;{interpretation.range.high} {interpretation.range.unit}
      </div>
      {interpretation.recommendation && (
        <div className="benchmark-recommendation">
          {interpretation.recommendation}
        </div>
      )}
    </div>
  )
}

export default BenchmarkIndicator
