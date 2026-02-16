import { Link } from 'react-router-dom'
import StatusBadge from './StatusBadge'
import styles from './VideoList.module.css'

function formatDate(dateStr) {
  const d = new Date(dateStr)
  return d.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatDuration(seconds) {
  if (!seconds) return ''
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  return `${m}:${String(s).padStart(2, '0')}`
}

export default function VideoList({ videos, onDelete }) {
  if (videos.length === 0) {
    return (
      <div className={styles.empty}>
        <p className={styles.emptyIcon}>&#127916;</p>
        <p className={styles.emptyText}>No videos yet</p>
        <p className={styles.emptyHint}>Paste some YouTube URLs above to get started</p>
      </div>
    )
  }

  return (
    <div className={styles.list}>
      {videos.map(video => (
        <div key={video.id} className={styles.card}>
          <div className={styles.cardMain}>
            <Link to={`/video/${video.id}`} className={styles.title}>
              {video.title || video.url}
            </Link>
            <div className={styles.meta}>
              <StatusBadge status={video.status} />
              {video.duration && (
                <span className={styles.duration}>{formatDuration(video.duration)}</span>
              )}
              <span className={styles.date}>{formatDate(video.created_at)}</span>
            </div>
            {video.status === 'failed' && video.error_message && (
              <p className={styles.error}>{video.error_message}</p>
            )}
          </div>
          <button
            className={styles.deleteBtn}
            onClick={() => onDelete(video.id)}
            title="Delete video"
          >
            &#10005;
          </button>
        </div>
      ))}
    </div>
  )
}
