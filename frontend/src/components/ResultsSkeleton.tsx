function ResultsSkeleton() {
  return (
    <div className="results-skeleton">
      <div className="skeleton-title"></div>

      <div className="skeleton-time"></div>

      <div className="skeleton-table">
        <div className="skeleton-header">
          <div className="skeleton-cell header-cell"></div>
          <div className="skeleton-cell header-cell"></div>
        </div>

        {/* Create 5 skeleton rows */}
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="skeleton-row">
            <div className="skeleton-cell"></div>
            <div className="skeleton-cell"></div>
          </div>
        ))}
      </div>

      <div className="skeleton-button"></div>
    </div>
  )
}

export default ResultsSkeleton
