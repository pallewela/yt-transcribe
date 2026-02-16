## Why

Users currently have to read the summary and key points visually. Adding a read-aloud capability lets users listen to the summary hands-free — useful for multitasking, accessibility, or quickly absorbing content without reading. The browser's built-in Web Speech Synthesis API makes this achievable with no backend changes or third-party dependencies.

## What Changes

- **Add a "Read Aloud" icon button** on the video detail page, positioned in the meta/status line next to the status badge and transcript source. Only visible for completed videos with a summary.
- **Speech playback controls**: When reading is active, the button area switches to show pause and stop icon buttons. Pause suspends speech and resumes on re-click; stop cancels speech and resets to the initial play icon.
- **Sequential reading order**: Reads the summary overview text first, then each key point's text sequentially.
- **Text highlighting during reading** (feature flag: `VITE_ENABLE_READING_HIGHLIGHT`): When enabled, the currently-being-read section (summary or individual key point) is visually highlighted in the UI as speech progresses. When disabled, speech plays without visual highlighting.
- **Graceful handling**: If the browser doesn't support `speechSynthesis`, the read-aloud button is hidden entirely. Speech is cancelled when navigating away from the page.

## Capabilities

### New Capabilities

- `read-aloud`: Text-to-speech playback of summary and key points using the Web Speech Synthesis API, with play/pause/stop controls and an optional text-highlighting mode behind a feature flag.

### Modified Capabilities

- `summary-dashboard`: The video detail page's status/meta line gains a new read-aloud icon button for completed videos.

## Impact

- **Frontend component**: `frontend/src/pages/VideoDetail.jsx` — add read-aloud button to meta line, integrate with speech hook, conditionally apply highlight styles.
- **Frontend hook**: New `frontend/src/hooks/useSpeechSynthesis.js` — encapsulates `window.speechSynthesis` API, manages utterance queue, exposes play/pause/stop/state.
- **Frontend styles**: `frontend/src/pages/VideoDetail.module.css` — new styles for the read-aloud button, active/paused states, and highlight class for the feature-flagged text highlighting.
- **Feature flag**: `VITE_ENABLE_READING_HIGHLIGHT` environment variable — controls whether text highlighting is active during speech. Defaults to `false`.
- **No backend changes**: Entirely client-side using the Web Speech Synthesis API.
- **No new dependencies**: Uses built-in browser APIs only.
- **Browser support**: Works in Chrome, Edge, Safari, Firefox. The button hides itself if `speechSynthesis` is unavailable.
