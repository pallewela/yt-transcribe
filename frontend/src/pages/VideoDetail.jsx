import { useState, useEffect, useMemo } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getVideo } from '../api'
import StatusBadge from '../components/StatusBadge'
import TimestampLink from '../components/TimestampLink'
import { youtubeUrlAtTime } from '../components/TimestampLink'
import useYouTubePlayer from '../hooks/useYouTubePlayer'
import useSpeechSynthesis from '../hooks/useSpeechSynthesis'
import styles from './VideoDetail.module.css'

const highlightEnabled = import.meta.env.VITE_ENABLE_READING_HIGHLIGHT === 'true'

function PlayIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="11 5 6 9 6 15 11 19 11 5" />
      <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
      <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
    </svg>
  )
}

function PauseIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="6" y="4" width="4" height="16" />
      <rect x="14" y="4" width="4" height="16" />
    </svg>
  )
}

function StopIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="4" y="4" width="16" height="16" rx="2" />
    </svg>
  )
}

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

  const showPlayer = video && video.status === 'completed'
  const { containerRef, isReady, error: playerError, seekTo } = useYouTubePlayer(
    showPlayer ? video.video_id : null
  )

  const summary = video ? video.summary_json : null

  const speechSegments = useMemo(() => {
    if (!summary) return []
    const parts = []
    if (summary.overview) parts.push(summary.overview)
    if (summary.key_points) {
      summary.key_points.forEach((kp) => parts.push(kp.text))
    }
    return parts
  }, [summary])

  const { play, pause, stop, state: speechState, activeIndex, isSupported: speechSupported } =
    useSpeechSynthesis(speechSegments)

  if (loading) return <p className={styles.loading}>Loading...</p>
  if (!video) return <p className={styles.loading}>Video not found</p>

  const segments = video.transcript_segments
  const showReadAloud = speechSupported && video.status === 'completed' && summary
  const isHighlighting = highlightEnabled && speechState !== 'idle'

  return (
    <div>
      <Link to="/" className={styles.back}>&larr; Back to dashboard</Link>

      <div className={styles.header}>
        <h1 className={styles.title}>
          <a
            href={`https://www.youtube.com/watch?v=${video.video_id}`}
            target="_blank"
            rel="noopener noreferrer"
            className={styles.titleLink}
          >
            {video.title || video.url}
          </a>
        </h1>
        <div className={styles.meta}>
          <StatusBadge status={video.status} />
          {video.transcript_source && (
            <span className={styles.source}>
              Transcript: {video.transcript_source === 'youtube_captions' ? 'YouTube Captions' : 'Whisper AI'}
            </span>
          )}
          {showReadAloud && speechState === 'idle' && (
            <button
              className={styles.readAloudBtn}
              onClick={play}
              title="Read aloud summary and key points"
            >
              <PlayIcon />
            </button>
          )}
          {showReadAloud && (speechState === 'playing' || speechState === 'paused') && (
            <div className={styles.readAloudControls}>
              <button
                className={styles.readAloudBtn}
                onClick={speechState === 'playing' ? pause : play}
                title={speechState === 'playing' ? 'Pause' : 'Resume'}
              >
                {speechState === 'playing' ? <PauseIcon /> : <PlayIcon />}
              </button>
              <button
                className={styles.readAloudBtn}
                onClick={stop}
                title="Stop"
              >
                <StopIcon />
              </button>
            </div>
          )}
        </div>
      </div>

      {showPlayer && (
        <div className={styles.playerWrapper}>
          {playerError ? (
            <div className={styles.playerFallback}>
              <p>Could not load video player.</p>
              <a
                href={youtubeUrlAtTime(video.video_id, 0)}
                target="_blank"
                rel="noopener noreferrer"
                className={styles.fallbackLink}
              >
                Watch on YouTube &rarr;
              </a>
            </div>
          ) : (
            <>
              <div ref={containerRef} className={styles.playerContainer} />
              {!isReady && (
                <div className={styles.playerLoading}>
                  <div className={styles.spinner} />
                  <span>Loading player...</span>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {video.status === 'completed' && summary && (
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Summary</h2>
          <p className={`${styles.overview}${isHighlighting && activeIndex === 0 ? ` ${styles.activeReading}` : ''}`}>
            {summary.overview}
          </p>
        </section>
      )}

      {video.status === 'completed' && summary && summary.key_points && summary.key_points.length > 0 && (
        <section className={styles.section}>
          <h3 className={styles.subTitle}>Key Points</h3>
          <div className={styles.keyPointsScroll}>
            <ul className={styles.pointsList}>
              {summary.key_points.map((kp, i) => (
                <li
                  key={i}
                  className={`${styles.point}${isHighlighting && activeIndex === i + 1 ? ` ${styles.activeReading}` : ''}`}
                >
                  <TimestampLink
                    videoId={video.video_id}
                    seconds={kp.timestamp}
                    onSeek={seekTo}
                  />
                  <span className={styles.pointText}>{kp.text}</span>
                </li>
              ))}
            </ul>
          </div>
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
                  <TimestampLink
                    videoId={video.video_id}
                    seconds={seg.start}
                    onSeek={seekTo}
                  />
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
