## Context

The video detail page (`/video/:id`) displays a summary overview and key points for completed videos. Currently there is no way to listen to this content. The proposal introduces a read-aloud feature using the browser's built-in Web Speech Synthesis API, with an optional text-highlighting mode controlled by a feature flag.

Key constraint: no backend changes, no new dependencies — purely client-side using `window.speechSynthesis`.

Current meta line in `VideoDetail.jsx` (line 62-69):
```
<div className={styles.meta}>
  <StatusBadge status={video.status} />
  <span className={styles.source}>Transcript: ...</span>
</div>
```

The read-aloud button will be added to this line.

## Goals / Non-Goals

**Goals:**
- Provide a play/pause/stop interface for reading aloud summary + key points via speech synthesis
- Read content sequentially: summary overview first, then each key point in order
- Support an optional text-highlighting mode (feature flag) that visually marks the currently-spoken section
- Gracefully degrade when `speechSynthesis` is unavailable
- Clean up speech on page navigation

**Non-Goals:**
- Reading the full transcript aloud (only summary + key points)
- Custom voice selection or speech rate controls (can be added later)
- Server-side TTS or audio file generation
- Supporting speech synthesis on non-completed videos

## Decisions

### 1. Custom hook `useSpeechSynthesis` to encapsulate all speech logic

**Decision**: Create `frontend/src/hooks/useSpeechSynthesis.js` that accepts an array of text segments and exposes `{ play, pause, stop, state, activeIndex, isSupported }`.

**Rationale**: Isolating speech synthesis in a hook keeps `VideoDetail.jsx` clean and makes the feature testable/reusable. The hook manages the `SpeechSynthesisUtterance` queue internally.

**Alternative considered**: Inline speech logic in the component. Rejected — mixes concerns and makes the component harder to maintain.

**Hook API design:**
- `useSpeechSynthesis(segments: string[])` — segments is the ordered array of texts to read
- `play()` — starts or resumes speech from the current position
- `pause()` — pauses speech (using `speechSynthesis.pause()`)
- `stop()` — cancels all speech and resets to beginning
- `state` — `'idle' | 'playing' | 'paused'`
- `activeIndex` — index of the segment currently being spoken (-1 when idle)
- `isSupported` — boolean, `false` if `window.speechSynthesis` is undefined

**Implementation approach**: Rather than queuing all utterances at once (which has browser bugs, especially Chrome's 15-second cutoff), create one `SpeechSynthesisUtterance` at a time. When `onend` fires, advance to the next segment and create a new utterance. This avoids Chrome's queue-based issues.

### 2. Segment mapping: summary overview = index 0, key points = indices 1..N

**Decision**: Build the segments array as `[summary.overview, ...summary.key_points.map(kp => kp.text)]`. The hook tracks `activeIndex` which maps directly to: 0 = summary, 1+ = key point at (index - 1).

**Rationale**: Simple flat array makes the hook generic. The component maps `activeIndex` to highlight the correct UI element.

### 3. Feature flag via Vite environment variable

**Decision**: Use `import.meta.env.VITE_ENABLE_READING_HIGHLIGHT === 'true'` to control text highlighting. Default to `false` (no `.env` entry needed to disable).

**Rationale**: Vite's `import.meta.env.VITE_*` pattern is the standard way to expose build-time feature flags in this project. No runtime config needed — it bakes in at build time.

### 4. Text highlighting implementation

**Decision**: When the feature flag is enabled and speech is playing, apply a CSS class (`styles.activeReading`) to the summary `<p>` or key point `<li>` that corresponds to `activeIndex`. The class adds a subtle background highlight and left border accent.

**Rationale**: CSS class toggling is the simplest approach. It requires no DOM manipulation — just a conditional `className` in React. The component checks `highlightEnabled && activeIndex === i` to apply the class.

**Alternative considered**: Scrolling the highlighted element into view automatically. Deferred — can be added later if useful, but may be disorienting.

### 5. Icon buttons using inline SVGs

**Decision**: Use small inline SVG icons for play (speaker/volume icon), pause, and stop buttons. No icon library dependency.

**Rationale**: Three simple icons don't justify adding an icon library. Inline SVGs are small, customizable, and keep the zero-dependency constraint.

### 6. Speech cleanup on unmount

**Decision**: The hook's cleanup function calls `speechSynthesis.cancel()` in its `useEffect` return, ensuring speech stops when the user navigates away.

**Rationale**: Without cleanup, speech continues playing even after leaving the page. This is the standard React pattern for resource cleanup.

## Risks / Trade-offs

- **Chrome 15-second utterance bug** → Mitigation: One utterance per segment (not queuing all at once). Individual summary/key-point texts are typically well under 15 seconds.
- **`speechSynthesis.pause()` not supported on all browsers** → Mitigation: If pause doesn't work, the pause button effectively becomes a no-op. The stop button always works as a fallback.
- **Feature flag requires rebuild to toggle** → Acceptable for now. The flag controls a visual enhancement, not core functionality. A runtime toggle could be added later.
- **Voice varies by OS/browser** → Acceptable. We use the system default voice. Users can change their OS speech settings if desired.
- **No speech rate control** → Keeping v1 simple. Can be added as a follow-up with a small speed selector.
