import { useState } from 'react'
import { submitVideos } from '../api'
import styles from './SubmitForm.module.css'

const YT_REGEX = /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?.*v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/shorts\/)[a-zA-Z0-9_-]{11}/

function validateUrls(text) {
  const lines = text.split('\n').map(l => l.trim()).filter(Boolean)
  return lines.map(url => ({
    url,
    valid: YT_REGEX.test(url),
  }))
}

export default function SubmitForm({ onSubmitted }) {
  const [input, setInput] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [feedback, setFeedback] = useState(null)

  const parsed = input.trim() ? validateUrls(input) : []
  const validCount = parsed.filter(p => p.valid).length
  const invalidCount = parsed.filter(p => !p.valid).length

  async function handleSubmit(e) {
    e.preventDefault()
    const urls = parsed.filter(p => p.valid).map(p => p.url)
    if (urls.length === 0) return

    setSubmitting(true)
    setFeedback(null)
    try {
      const result = await submitVideos(urls)
      const succeeded = result.results.filter(r => r.success).length
      const failed = result.results.filter(r => !r.success).length
      setFeedback({
        type: 'success',
        message: `${succeeded} video${succeeded !== 1 ? 's' : ''} queued${failed > 0 ? `, ${failed} failed` : ''}`,
      })
      setInput('')
      onSubmitted?.()
    } catch (err) {
      setFeedback({
        type: 'error',
        message: err.response?.data?.detail || 'Failed to submit videos',
      })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <textarea
        className={styles.textarea}
        value={input}
        onChange={e => setInput(e.target.value)}
        placeholder="Paste YouTube URLs here (one per line)&#10;&#10;https://www.youtube.com/watch?v=...&#10;https://youtu.be/..."
        rows={4}
      />
      <div className={styles.bar}>
        <div className={styles.validation}>
          {parsed.length > 0 && (
            <>
              {validCount > 0 && (
                <span className={styles.validBadge}>{validCount} valid</span>
              )}
              {invalidCount > 0 && (
                <span className={styles.invalidBadge}>{invalidCount} invalid</span>
              )}
            </>
          )}
        </div>
        <button
          type="submit"
          disabled={validCount === 0 || submitting}
          className={styles.button}
        >
          {submitting ? 'Submitting...' : `Submit ${validCount > 0 ? validCount : ''} video${validCount !== 1 ? 's' : ''}`}
        </button>
      </div>
      {feedback && (
        <div className={`${styles.feedback} ${styles[feedback.type]}`}>
          {feedback.message}
        </div>
      )}
    </form>
  )
}
