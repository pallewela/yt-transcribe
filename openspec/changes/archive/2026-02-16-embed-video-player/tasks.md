## 1. YouTube Player Hook

- [x] 1.1 Create `frontend/src/hooks/useYouTubePlayer.js` that loads the YouTube IFrame API script dynamically (idempotent — only loads once)
- [x] 1.2 Implement player creation in the hook: accept a container ref and `videoId`, create a `YT.Player` instance on `onYouTubeIframeAPIReady`
- [x] 1.3 Expose `seekTo(seconds)` function from the hook that calls `player.seekTo(seconds, true)` and starts playback
- [x] 1.4 Expose `isReady` and `error` state from the hook for loading/error UI
- [x] 1.5 Handle cleanup on unmount (destroy player instance)

## 2. TimestampLink Component Update

- [x] 2.1 Add optional `onSeek` callback prop to `TimestampLink` component
- [x] 2.2 When `onSeek` is provided, render a `<button>` that calls `onSeek(seconds)` instead of an `<a>` tag
- [x] 2.3 Style the button to match the existing timestamp link appearance
- [x] 2.4 When `onSeek` is absent, preserve the existing external link behavior (backward compatible)

## 3. VideoDetail Page Layout Restructure

- [x] 3.1 Restructure `VideoDetail.jsx` into a two-column layout: left column for sticky player, right column for scrollable content (header, summary, key points, transcript)
- [x] 3.2 Add the embedded player container div in the left column with a ref for the hook
- [x] 3.3 Initialize `useYouTubePlayer` hook with the video's `video_id` and container ref
- [x] 3.4 Show a loading placeholder in the player area while `isReady` is false
- [x] 3.5 Show a fallback message with direct YouTube link when `error` is set

## 4. Wire Timestamp Seeking

- [x] 4.1 Pass the hook's `seekTo` function as the `onSeek` prop to all `TimestampLink` components in the key points section
- [x] 4.2 Pass the hook's `seekTo` function as the `onSeek` prop to all `TimestampLink` components in the transcript section

## 5. CSS Styling

- [x] 5.1 Update `VideoDetail.module.css` with a two-column CSS grid layout (player left, content right)
- [x] 5.2 Add `position: sticky; top: <offset>` to the player column so it stays visible during scroll
- [x] 5.3 Set the player aspect ratio (16:9) and appropriate max-width
- [x] 5.4 Add responsive breakpoint at 768px: collapse to single column with sticky player at top
- [x] 5.5 Style the player loading placeholder and error fallback states

## 6. Verification

- [x] 6.1 Verify player renders correctly for completed videos and is hidden for queued/processing/failed videos
- [x] 6.2 Verify clicking key point timestamps seeks the embedded player without opening a new tab
- [x] 6.3 Verify clicking transcript timestamps seeks the embedded player without opening a new tab
- [x] 6.4 Verify sticky behavior: player stays visible while scrolling through long content on desktop
- [x] 6.5 Verify responsive layout: single-column with sticky top player on narrow viewports
