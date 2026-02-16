## 1. Create `useSpeechSynthesis` hook

- [x] 1.1 Create `frontend/src/hooks/useSpeechSynthesis.js` that accepts an array of text segments
- [x] 1.2 Implement `isSupported` check (`typeof window !== 'undefined' && 'speechSynthesis' in window`)
- [x] 1.3 Implement `play()` — create a `SpeechSynthesisUtterance` for the current segment, call `speechSynthesis.speak()`, set state to `'playing'`
- [x] 1.4 Implement `pause()` — call `speechSynthesis.pause()`, set state to `'paused'`
- [x] 1.5 Implement `stop()` — call `speechSynthesis.cancel()`, reset `activeIndex` to -1, set state to `'idle'`
- [x] 1.6 Implement segment advancement — on utterance `onend`, increment `activeIndex` and start the next segment; when all segments are done, reset to `'idle'`
- [x] 1.7 Implement resume — when state is `'paused'` and `play()` is called, call `speechSynthesis.resume()`
- [x] 1.8 Add cleanup `useEffect` that calls `speechSynthesis.cancel()` on unmount

## 2. Add read-aloud button to VideoDetail

- [x] 2.1 Import `useSpeechSynthesis` in `VideoDetail.jsx`
- [x] 2.2 Build the segments array: `[summary.overview, ...summary.key_points.map(kp => kp.text)]` when summary is available
- [x] 2.3 Call the hook with the segments array
- [x] 2.4 Add a read-aloud icon button to the `<div className={styles.meta}>` line, after the transcript source — only render when `isSupported && video.status === 'completed' && summary`
- [x] 2.5 When state is `'idle'`, show a play/speaker icon button that calls `play()`
- [x] 2.6 When state is `'playing'`, show pause and stop icon buttons
- [x] 2.7 When state is `'paused'`, show resume (play) and stop icon buttons

## 3. Add inline SVG icons

- [x] 3.1 Create a play/speaker SVG icon (small, ~16-20px)
- [x] 3.2 Create a pause SVG icon
- [x] 3.3 Create a stop SVG icon
- [x] 3.4 Style the icon buttons (no background, subtle hover effect, inline with meta line)

## 4. Implement text highlighting (feature flag)

- [x] 4.1 Read the feature flag: `const highlightEnabled = import.meta.env.VITE_ENABLE_READING_HIGHLIGHT === 'true'`
- [x] 4.2 When `highlightEnabled && state !== 'idle'`, apply `styles.activeReading` class to the summary `<p>` when `activeIndex === 0`
- [x] 4.3 When `highlightEnabled && state !== 'idle'`, apply `styles.activeReading` class to the key point `<li>` at index `activeIndex - 1`
- [x] 4.4 Add `.activeReading` CSS class in `VideoDetail.module.css` with a subtle background highlight and left border accent
- [x] 4.5 Ensure highlights are removed when state returns to `'idle'`

## 5. Add CSS styles

- [x] 5.1 Add `.readAloudBtn` styles for the icon button (inline flex, no border, cursor pointer, subtle hover)
- [x] 5.2 Add `.readAloudControls` wrapper style to group pause/stop buttons inline in the meta line
- [x] 5.3 Add `.activeReading` highlight style (background tint + left border accent)

## 6. Verify behavior

- [x] 6.1 Verify the read-aloud button appears for completed videos with a summary
- [x] 6.2 Verify the button is hidden for queued/processing/failed videos
- [x] 6.3 Verify clicking play starts speaking the summary, then key points
- [x] 6.4 Verify pause suspends speech and resume continues
- [x] 6.5 Verify stop cancels speech and resets controls
- [x] 6.6 Verify speech stops when navigating away from the page
- [x] 6.7 Verify text highlighting works when `VITE_ENABLE_READING_HIGHLIGHT=true`
- [x] 6.8 Verify no highlighting when the flag is off or absent
