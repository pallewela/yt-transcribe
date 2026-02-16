import { useState, useRef, useCallback, useEffect } from 'react'

const isSupported =
  typeof window !== 'undefined' && 'speechSynthesis' in window

export default function useSpeechSynthesis(segments) {
  const [state, setState] = useState('idle')
  const [activeIndex, setActiveIndex] = useState(-1)
  const utteranceRef = useRef(null)
  const indexRef = useRef(-1)
  const segmentsRef = useRef(segments)

  segmentsRef.current = segments

  const speakSegment = useCallback((index) => {
    if (!isSupported) return
    if (index >= segmentsRef.current.length) {
      setState('idle')
      setActiveIndex(-1)
      indexRef.current = -1
      return
    }

    const utterance = new SpeechSynthesisUtterance(segmentsRef.current[index])
    utterance.onend = () => {
      const next = indexRef.current + 1
      indexRef.current = next
      setActiveIndex(next)
      speakSegment(next)
    }
    utterance.onerror = (e) => {
      if (e.error === 'canceled' || e.error === 'interrupted') return
      setState('idle')
      setActiveIndex(-1)
      indexRef.current = -1
    }

    utteranceRef.current = utterance
    window.speechSynthesis.speak(utterance)
  }, [])

  const play = useCallback(() => {
    if (!isSupported) return

    if (state === 'paused') {
      window.speechSynthesis.resume()
      setState('playing')
      return
    }

    window.speechSynthesis.cancel()
    indexRef.current = 0
    setActiveIndex(0)
    setState('playing')
    speakSegment(0)
  }, [state, speakSegment])

  const pause = useCallback(() => {
    if (!isSupported) return
    window.speechSynthesis.pause()
    setState('paused')
  }, [])

  const stop = useCallback(() => {
    if (!isSupported) return
    window.speechSynthesis.cancel()
    utteranceRef.current = null
    indexRef.current = -1
    setActiveIndex(-1)
    setState('idle')
  }, [])

  useEffect(() => {
    return () => {
      if (isSupported) {
        window.speechSynthesis.cancel()
      }
    }
  }, [])

  return { play, pause, stop, state, activeIndex, isSupported }
}
