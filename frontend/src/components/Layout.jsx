import { Link } from 'react-router-dom'
import styles from './Layout.module.css'

export default function Layout({ children }) {
  return (
    <div className={styles.wrapper}>
      <header className={styles.header}>
        <Link to="/" className={styles.logo}>
          <span className={styles.logoIcon}>&#9654;</span>
          YT Transcribe
        </Link>
        <p className={styles.tagline}>Transcribe &amp; summarize YouTube videos</p>
      </header>
      <main className={styles.main}>
        {children}
      </main>
    </div>
  )
}
