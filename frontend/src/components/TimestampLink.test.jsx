import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import TimestampLink, { formatTimestamp, youtubeUrlAtTime } from './TimestampLink'

describe('formatTimestamp', () => {
  it('formats seconds into m:ss', () => {
    expect(formatTimestamp(0)).toBe('0:00')
    expect(formatTimestamp(65)).toBe('1:05')
    expect(formatTimestamp(125.7)).toBe('2:05')
  })

  it('formats hours when >= 3600', () => {
    expect(formatTimestamp(3661)).toBe('1:01:01')
    expect(formatTimestamp(7200)).toBe('2:00:00')
  })
})

describe('youtubeUrlAtTime', () => {
  it('generates correct YouTube URL with time', () => {
    const url = youtubeUrlAtTime('abc123', 65.5)
    expect(url).toBe('https://www.youtube.com/watch?v=abc123&t=65s')
  })
})

describe('TimestampLink', () => {
  it('renders as an external link when onSeek is not provided', () => {
    render(<TimestampLink videoId="abc123" seconds={65} />)
    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('href', 'https://www.youtube.com/watch?v=abc123&t=65s')
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveTextContent('1:05')
  })

  it('renders as a button when onSeek is provided', () => {
    const onSeek = vi.fn()
    render(<TimestampLink videoId="abc123" seconds={65} onSeek={onSeek} />)
    const button = screen.getByRole('button')
    expect(button).toHaveTextContent('1:05')
    expect(screen.queryByRole('link')).toBeNull()
  })

  it('calls onSeek with seconds when button is clicked', () => {
    const onSeek = vi.fn()
    render(<TimestampLink videoId="abc123" seconds={65} onSeek={onSeek} />)
    fireEvent.click(screen.getByRole('button'))
    expect(onSeek).toHaveBeenCalledWith(65)
    expect(onSeek).toHaveBeenCalledTimes(1)
  })

  it('renders custom children', () => {
    render(<TimestampLink videoId="abc123" seconds={0}>Start</TimestampLink>)
    expect(screen.getByRole('link')).toHaveTextContent('Start')
  })

  it('has correct title attribute', () => {
    render(<TimestampLink videoId="abc123" seconds={125} />)
    expect(screen.getByRole('link')).toHaveAttribute('title', 'Jump to 2:05 in video')
  })

  it('has correct title attribute when onSeek is provided', () => {
    const onSeek = vi.fn()
    render(<TimestampLink videoId="abc123" seconds={125} onSeek={onSeek} />)
    expect(screen.getByRole('button')).toHaveAttribute('title', 'Jump to 2:05 in video')
  })
})
