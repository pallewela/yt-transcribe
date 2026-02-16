import { useEffect, useRef, useState, useCallback } from 'react'

let apiLoadPromise = null

function loadYouTubeAPI() {
  if (apiLoadPromise) return apiLoadPromise
  if (window.YT && window.YT.Player) return Promise.resolve()

  apiLoadPromise = new Promise((resolve, reject) => {
    const existing = document.querySelector('script[src*="youtube.com/iframe_api"]')
    if (existing) {
      const check = setInterval(() => {
        if (window.YT && window.YT.Player) {
          clearInterval(check)
          resolve()
        }
      }, 100)
      return
    }

    window.onYouTubeIframeAPIReady = () => resolve()

    const script = document.createElement('script')
    script.src = 'https://www.youtube.com/iframe_api'
    script.onerror = () => {
      apiLoadPromise = null
      reject(new Error('Failed to load YouTube IFrame API'))
    }
    document.head.appendChild(script)
  })

  return apiLoadPromise
}

export default function useYouTubePlayer(videoId) {
  const containerRef = useRef(null)
  const playerRef = useRef(null)
  const [isReady, setIsReady] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!videoId || !containerRef.current) return

    let destroyed = false

    async function init() {
      try {
        await loadYouTubeAPI()
        if (destroyed) return

        const el = document.createElement('div')
        containerRef.current.innerHTML = ''
        containerRef.current.appendChild(el)

        playerRef.current = new window.YT.Player(el, {
          videoId,
          playerVars: {
            autoplay: 0,
            modestbranding: 1,
            rel: 0,
            origin: window.location.origin,
          },
          events: {
            onReady: () => {
              if (!destroyed) setIsReady(true)
            },
            onError: (e) => {
              if (!destroyed) setError(`YouTube player error (code ${e.data})`)
            },
          },
        })
      } catch (err) {
        if (!destroyed) setError(err.message)
      }
    }

    init()

    return () => {
      destroyed = true
      if (playerRef.current && typeof playerRef.current.destroy === 'function') {
        playerRef.current.destroy()
      }
      playerRef.current = null
      setIsReady(false)
      setError(null)
    }
  }, [videoId])

  const seekTo = useCallback((seconds) => {
    if (playerRef.current && typeof playerRef.current.seekTo === 'function') {
      playerRef.current.seekTo(seconds, true)
      playerRef.current.playVideo()
    }
  }, [])

  return { containerRef, isReady, error, seekTo }
}
