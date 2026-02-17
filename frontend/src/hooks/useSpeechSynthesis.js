import { useState, useRef, useCallback, useEffect } from 'react'

const isSupported =
  typeof window !== 'undefined' && 'speechSynthesis' in window

function getPreferredVoice() {
  if (!isSupported) return null
  const voices = window.speechSynthesis.getVoices()
  return (
    voices.find((v) => v.name === 'Google US English') ||
    voices.find((v) => v.lang === 'en-US' && v.name.includes('Google')) ||
    null
  )
}

let voicePromise = null
function ensureVoice() {
  if (!isSupported) return Promise.resolve(null)
  const cached = getPreferredVoice()
  if (cached) return Promise.resolve(cached)
  if (voicePromise) return voicePromise
  voicePromise = new Promise((resolve) => {
    const handler = () => {
      const voice = getPreferredVoice()
      if (voice) {
        window.speechSynthesis.removeEventListener('voiceschanged', handler)
        voicePromise = null
        resolve(voice)
      }
    }
    window.speechSynthesis.addEventListener('voiceschanged', handler)
    setTimeout(() => {
      window.speechSynthesis.removeEventListener('voiceschanged', handler)
      voicePromise = null
      resolve(getPreferredVoice())
    }, 2000)
  })
  return voicePromise
}

export default function useSpeechSynthesis(segments) {
  const [state, setState] = useState('idle')
  const [activeIndex, setActiveIndex] = useState(-1)
  const utteranceRef = useRef(null)
  const indexRef = useRef(-1)
  const segmentsRef = useRef(segments)
  const voiceRef = useRef(null)

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
    if (voiceRef.current) {
      utterance.voice = voiceRef.current
    }
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
    setState('playing')

    ensureVoice().then((voice) => {
      voiceRef.current = voice
      indexRef.current = 0
      setActiveIndex(0)
      speakSegment(0)
    })
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
