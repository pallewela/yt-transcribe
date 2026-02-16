import { useState, useEffect, useCallback } from 'react'
import SubmitForm from '../components/SubmitForm'
import VideoList from '../components/VideoList'
import { getVideos, deleteVideo } from '../api'
import styles from './Dashboard.module.css'

const FILTERS = ['all', 'queued', 'processing', 'completed', 'failed']
const POLL_INTERVAL = 5000

export default function Dashboard() {
  const [videos, setVideos] = useState([])
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)

  const fetchVideos = useCallback(async () => {
    try {
      const data = await getVideos(filter === 'all' ? null : filter)
      setVideos(data)
    } catch (err) {
      console.error('Failed to fetch videos:', err)
    } finally {
      setLoading(false)
    }
  }, [filter])

  useEffect(() => {
    fetchVideos()
    const interval = setInterval(fetchVideos, POLL_INTERVAL)
    return () => clearInterval(interval)
  }, [fetchVideos])

  async function handleDelete(id) {
    if (!confirm('Delete this video and all its data?')) return
    try {
      await deleteVideo(id)
      setVideos(prev => prev.filter(v => v.id !== id))
    } catch (err) {
      console.error('Failed to delete video:', err)
    }
  }

  return (
    <div>
      <SubmitForm onSubmitted={fetchVideos} />

      <div className={styles.filterBar}>
        {FILTERS.map(f => (
          <button
            key={f}
            className={`${styles.filterBtn} ${filter === f ? styles.active : ''}`}
            onClick={() => setFilter(f)}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {loading ? (
        <p className={styles.loading}>Loading...</p>
      ) : (
        <VideoList videos={videos} onDelete={handleDelete} />
      )}
    </div>
  )
}
