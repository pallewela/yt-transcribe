import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getVideo } from '../api'
import StatusBadge from '../components/StatusBadge'
import TimestampLink from '../components/TimestampLink'
import styles from './VideoDetail.module.css'

export default function VideoDetail() {
  const { id } = useParams()
  const [video, setVideo] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showTranscript, setShowTranscript] = useState(false)

  useEffect(() => {
    let cancelled = false
    async function fetch() {
      try {
        const data = await getVideo(id)
        if (!cancelled) setVideo(data)
      } catch (err) {
        console.error('Failed to fetch video:', err)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    fetch()
    const interval = setInterval(fetch, 5000)
    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [id])

  if (loading) return <p className={styles.loading}>Loading...</p>
  if (!video) return <p className={styles.loading}>Video not found</p>

  const summary = video.summary_json
  const segments = video.transcript_segments

  return (
    <div>
      <Link to="/" className={styles.back}>&larr; Back to dashboard</Link>

      <div className={styles.header}>
        <h1 className={styles.title}>{video.title || video.url}</h1>
        <div className={styles.meta}>
          <StatusBadge status={video.status} />
          {video.transcript_source && (
            <span className={styles.source}>
              Transcript: {video.transcript_source === 'youtube_captions' ? 'YouTube Captions' : 'Whisper AI'}
            </span>
          )}
        </div>
      </div>

      {video.status === 'completed' && summary && (
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Summary</h2>
          <p className={styles.overview}>{summary.overview}</p>

          {summary.key_points && summary.key_points.length > 0 && (
            <div className={styles.keyPoints}>
              <h3 className={styles.subTitle}>Key Points</h3>
              <ul className={styles.pointsList}>
                {summary.key_points.map((kp, i) => (
                  <li key={i} className={styles.point}>
                    <TimestampLink videoId={video.video_id} seconds={kp.timestamp} />
                    <span className={styles.pointText}>{kp.text}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}

      {video.status === 'failed' && video.error_message && (
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Error</h2>
          <p className={styles.error}>{video.error_message}</p>
        </section>
      )}

      {(video.status === 'queued' || video.status === 'processing') && (
        <section className={styles.section}>
          <p className={styles.pending}>
            {video.status === 'queued'
              ? 'This video is queued for processing. It will be transcribed and summarized shortly.'
              : 'This video is currently being processed. Please wait...'}
          </p>
        </section>
      )}

      {segments && segments.length > 0 && (
        <section className={styles.section}>
          <button
            className={styles.toggleBtn}
            onClick={() => setShowTranscript(!showTranscript)}
          >
            {showTranscript ? 'Hide' : 'Show'} Full Transcript ({segments.length} segments)
          </button>

          {showTranscript && (
            <div className={styles.transcript}>
              {segments.map((seg, i) => (
                <div key={i} className={styles.segment}>
                  <TimestampLink videoId={video.video_id} seconds={seg.start} />
                  <span className={styles.segText}>{seg.text}</span>
                </div>
              ))}
            </div>
          )}
        </section>
      )}
    </div>
  )
}
