import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

vi.mock('../api', () => ({
  getVideo: vi.fn(),
}))

vi.mock('../hooks/useYouTubePlayer', () => ({
  default: vi.fn(() => ({
    containerRef: { current: null },
    isReady: true,
    error: null,
    seekTo: vi.fn(),
  })),
}))

import { getVideo } from '../api'
import useYouTubePlayer from '../hooks/useYouTubePlayer'
import VideoDetail from './VideoDetail'

function renderWithRouter(videoId = '1') {
  return render(
    <MemoryRouter initialEntries={[`/videos/${videoId}`]}>
      <Routes>
        <Route path="/videos/:id" element={<VideoDetail />} />
      </Routes>
    </MemoryRouter>
  )
}

const completedVideo = {
  id: 1,
  url: 'https://youtu.be/abc12345678',
  video_id: 'abc12345678',
  title: 'Test Video Title',
  status: 'completed',
  transcript_source: 'youtube_captions',
  transcript_segments: [
    { start: 0, text: 'Hello world' },
    { start: 30.5, text: 'Second segment' },
  ],
  summary_json: {
    overview: 'This is the summary overview.',
    key_points: [
      { timestamp: 0, text: 'First key point' },
      { timestamp: 30, text: 'Second key point' },
    ],
  },
}

const queuedVideo = {
  id: 2,
  url: 'https://youtu.be/def12345678',
  video_id: 'def12345678',
  title: 'Queued Video',
  status: 'queued',
  transcript_segments: null,
  summary_json: null,
}

describe('VideoDetail', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows loading state initially', () => {
    getVideo.mockReturnValue(new Promise(() => {}))
    renderWithRouter()
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('shows player for completed video', async () => {
    getVideo.mockResolvedValue(completedVideo)
    renderWithRouter()

    expect(await screen.findByText('Test Video Title')).toBeInTheDocument()
    expect(useYouTubePlayer).toHaveBeenCalledWith('abc12345678')
  })

  it('does not create player for queued video', async () => {
    getVideo.mockResolvedValue(queuedVideo)
    renderWithRouter('2')

    expect(await screen.findByText('Queued Video')).toBeInTheDocument()
    expect(useYouTubePlayer).toHaveBeenCalledWith(null)
  })

  it('renders summary key points as buttons with onSeek', async () => {
    const mockSeekTo = vi.fn()
    useYouTubePlayer.mockReturnValue({
      containerRef: { current: null },
      isReady: true,
      error: null,
      seekTo: mockSeekTo,
    })

    getVideo.mockResolvedValue(completedVideo)
    renderWithRouter()

    await screen.findByText('Test Video Title')
    expect(screen.getByText('This is the summary overview.')).toBeInTheDocument()
    expect(screen.getByText('First key point')).toBeInTheDocument()
    expect(screen.getByText('Second key point')).toBeInTheDocument()

    const buttons = screen.getAllByTitle(/Jump to/)
    expect(buttons.length).toBeGreaterThanOrEqual(2)
    fireEvent.click(buttons[0])
    expect(mockSeekTo).toHaveBeenCalledWith(0)
  })

  it('renders transcript timestamps as seek buttons', async () => {
    const mockSeekTo = vi.fn()
    useYouTubePlayer.mockReturnValue({
      containerRef: { current: null },
      isReady: true,
      error: null,
      seekTo: mockSeekTo,
    })

    getVideo.mockResolvedValue(completedVideo)
    renderWithRouter()

    await screen.findByText('Test Video Title')

    const toggleBtn = screen.getByText(/Show Full Transcript/)
    fireEvent.click(toggleBtn)

    expect(screen.getByText('Hello world')).toBeInTheDocument()
    expect(screen.getByText('Second segment')).toBeInTheDocument()
  })

  it('shows fallback when player has error', async () => {
    useYouTubePlayer.mockReturnValue({
      containerRef: { current: null },
      isReady: false,
      error: 'Failed to load YouTube IFrame API',
      seekTo: vi.fn(),
    })

    getVideo.mockResolvedValue(completedVideo)
    renderWithRouter()

    await screen.findByText('Test Video Title')
    expect(screen.getByText('Could not load video player.')).toBeInTheDocument()
    expect(screen.getByText(/Watch on YouTube/)).toBeInTheDocument()
  })

  it('shows loading placeholder when player is not ready', async () => {
    useYouTubePlayer.mockReturnValue({
      containerRef: { current: null },
      isReady: false,
      error: null,
      seekTo: vi.fn(),
    })

    getVideo.mockResolvedValue(completedVideo)
    renderWithRouter()

    await screen.findByText('Test Video Title')
    expect(screen.getByText('Loading player...')).toBeInTheDocument()
  })

  it('shows pending message for queued videos', async () => {
    getVideo.mockResolvedValue(queuedVideo)
    renderWithRouter('2')

    expect(await screen.findByText(/queued for processing/)).toBeInTheDocument()
  })

  it('shows error message for failed videos', async () => {
    getVideo.mockResolvedValue({
      ...queuedVideo,
      status: 'failed',
      error_message: 'Transcription failed',
    })

    renderWithRouter('2')
    expect(await screen.findByText('Transcription failed')).toBeInTheDocument()
  })
})
