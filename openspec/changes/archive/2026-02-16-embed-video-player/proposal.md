## Why

When users view a video summary, clicking a timestamp opens the YouTube video in a new browser tab. This breaks the user's flow — they lose context, must switch tabs, and cannot easily reference the summary alongside the video. Embedding the video directly in the detail page and linking timestamps to in-page seek operations will create a seamless, integrated viewing experience.

## What Changes

- Embed a YouTube iframe player on the video detail page using the YouTube IFrame Player API
- Replace timestamp link behavior in the key points section: instead of opening a new tab, clicking a timestamp seeks the embedded player to that time
- Redesign the video detail page layout so the embedded player is sticky (remains visible) while the user scrolls through the summary key points and transcript
- Transcript timestamp clicks should also seek the embedded player rather than opening a new tab

## Capabilities

### New Capabilities
- `embedded-player`: Covers the YouTube IFrame Player embed, player API integration for programmatic seeking, and the sticky layout that keeps the player visible during scrolling

### Modified Capabilities
- `summary-dashboard`: Timestamp click behavior changes from "open YouTube in new tab" to "seek embedded player to time". Applies to both key point timestamps and transcript segment timestamps.

## Impact

- **Frontend only** — no backend or API changes required
- `frontend/src/pages/VideoDetail.jsx` — major restructuring for the two-panel sticky layout with embedded player
- `frontend/src/pages/VideoDetail.module.css` — new styles for sticky player container and scrollable content area
- `frontend/src/components/TimestampLink.jsx` — behavior changes from external link to onClick seek handler
- New dependency on [YouTube IFrame Player API](https://developers.google.com/youtube/iframe_api_reference) (loaded via script tag, no npm package needed)
