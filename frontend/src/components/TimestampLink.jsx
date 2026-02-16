import styles from './TimestampLink.module.css'

export function formatTimestamp(seconds) {
  const s = Math.floor(seconds)
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = s % 60
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
  return `${m}:${String(sec).padStart(2, '0')}`
}

export function youtubeUrlAtTime(videoId, seconds) {
  return `https://www.youtube.com/watch?v=${videoId}&t=${Math.floor(seconds)}s`
}

export default function TimestampLink({ videoId, seconds, children }) {
  const url = youtubeUrlAtTime(videoId, seconds)
  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className={styles.link}
      title={`Jump to ${formatTimestamp(seconds)} in video`}
    >
      {children || formatTimestamp(seconds)}
    </a>
  )
}
