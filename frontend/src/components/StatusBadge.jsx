import styles from './StatusBadge.module.css'

const STATUS_MAP = {
  queued: { label: 'Queued', className: 'queued' },
  processing: { label: 'Processing', className: 'processing' },
  completed: { label: 'Completed', className: 'completed' },
  failed: { label: 'Failed', className: 'failed' },
}

export default function StatusBadge({ status }) {
  const config = STATUS_MAP[status] || { label: status, className: 'queued' }
  return (
    <span className={`${styles.badge} ${styles[config.className]}`}>
      {config.label}
    </span>
  )
}
