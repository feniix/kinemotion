import { RecentUpload } from '../hooks/useRecentUploads'

interface RecentUploadsProps {
  uploads: RecentUpload[]
  onSelect: (filename: string, jumpType: 'cmj' | 'dropjump') => void
  onClear: () => void
}

function RecentUploads({ uploads, onSelect, onClear }: RecentUploadsProps) {
  if (uploads.length === 0) {
    return null
  }

  const formatTime = (timestamp: number): string => {
    const now = Date.now()
    const diff = now - timestamp
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))

    if (hours > 0) {
      return `${hours}h ago`
    }
    if (minutes > 0) {
      return `${minutes}m ago`
    }
    return 'Just now'
  }

  const formatJumpType = (type: string): string => {
    return type === 'cmj' ? 'CMJ' : 'Drop Jump'
  }

  return (
    <div className="recent-uploads">
      <div className="recent-header">
        <h4>Recent Uploads</h4>
        <button onClick={onClear} className="clear-button" title="Clear history">
          Clear
        </button>
      </div>
      <div className="recent-list">
        {uploads.map(upload => (
          <button
            key={upload.id}
            onClick={() => onSelect(upload.filename, upload.jumpType)}
            className="recent-item"
            title={`Re-upload: ${upload.filename}`}
          >
            <span className="recent-filename">{upload.filename}</span>
            <span className="recent-meta">
              <span className="recent-type">{formatJumpType(upload.jumpType)}</span>
              <span className="recent-time">{formatTime(upload.timestamp)}</span>
            </span>
          </button>
        ))}
      </div>
    </div>
  )
}

export default RecentUploads
