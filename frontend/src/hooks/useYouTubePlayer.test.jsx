import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, act, screen } from '@testing-library/react'
import { useRef, useEffect } from 'react'
import useYouTubePlayer from './useYouTubePlayer'

let latestHookResult = null

function TestHarness({ videoId }) {
  const hook = useYouTubePlayer(videoId)
  const divRef = useRef(null)

  useEffect(() => {
    if (divRef.current) {
      hook.containerRef.current = divRef.current
    }
  })

  latestHookResult = hook
  return <div ref={divRef} data-testid="player-container" />
}

function PlayerWithContainer({ videoId }) {
  const hook = useYouTubePlayer(videoId)
  latestHookResult = hook

  return (
    <div>
      <div ref={hook.containerRef} data-testid="player-container" />
      <span data-testid="is-ready">{String(hook.isReady)}</span>
      <span data-testid="error">{hook.error || ''}</span>
    </div>
  )
}

describe('useYouTubePlayer', () => {
  let mockPlayer

  beforeEach(() => {
    latestHookResult = null
    mockPlayer = {
      seekTo: vi.fn(),
      playVideo: vi.fn(),
      destroy: vi.fn(),
    }

    window.YT = {
      Player: function MockPlayer(el, opts) {
        setTimeout(() => opts.events.onReady(), 0)
        return mockPlayer
      },
    }
  })

  afterEach(() => {
    delete window.YT
    document.querySelectorAll('script[src*="youtube"]').forEach(s => s.remove())
    delete window.onYouTubeIframeAPIReady
  })

  it('returns isReady=false and no error initially', () => {
    render(<PlayerWithContainer videoId={null} />)
    expect(screen.getByTestId('is-ready')).toHaveTextContent('false')
    expect(screen.getByTestId('error')).toHaveTextContent('')
  })

  it('does not create player when videoId is null', () => {
    const spy = vi.spyOn(window.YT, 'Player')
    render(<PlayerWithContainer videoId={null} />)
    expect(spy).not.toHaveBeenCalled()
  })

  it('creates player and sets isReady when videoId is provided', async () => {
    render(<PlayerWithContainer videoId="testVideoId" />)

    await act(async () => {
      await new Promise(r => setTimeout(r, 50))
    })

    expect(screen.getByTestId('is-ready')).toHaveTextContent('true')
    expect(screen.getByTestId('error')).toHaveTextContent('')
  })

  it('seekTo calls player.seekTo and playVideo', async () => {
    render(<PlayerWithContainer videoId="testVideoId" />)

    await act(async () => {
      await new Promise(r => setTimeout(r, 50))
    })

    act(() => {
      latestHookResult.seekTo(42.5)
    })

    expect(mockPlayer.seekTo).toHaveBeenCalledWith(42.5, true)
    expect(mockPlayer.playVideo).toHaveBeenCalled()
  })

  it('sets error when YT.Player fires onError', async () => {
    window.YT = {
      Player: function MockErrorPlayer(el, opts) {
        setTimeout(() => opts.events.onError({ data: 150 }), 0)
        return mockPlayer
      },
    }

    render(<PlayerWithContainer videoId="badVideoId" />)

    await act(async () => {
      await new Promise(r => setTimeout(r, 50))
    })

    expect(screen.getByTestId('error')).toHaveTextContent('YouTube player error (code 150)')
    expect(screen.getByTestId('is-ready')).toHaveTextContent('false')
  })

  it('destroys player on unmount', async () => {
    const { unmount } = render(<PlayerWithContainer videoId="testVideoId" />)

    await act(async () => {
      await new Promise(r => setTimeout(r, 50))
    })

    unmount()
    expect(mockPlayer.destroy).toHaveBeenCalled()
  })
})
