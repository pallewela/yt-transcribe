## Context

The video detail page (`VideoDetail.jsx`) currently displays the summary, key points with timestamps, and full transcript. Clicking any timestamp opens the YouTube video in a new browser tab using `?t=` URL parameters. This forces a context switch — the user loses sight of the summary to watch the video.

The page is a single scrollable column. The `TimestampLink` component renders `<a>` tags pointing to external YouTube URLs.

## Goals / Non-Goals

**Goals:**
- Embed a YouTube video player directly on the video detail page
- Make timestamp clicks in key points and transcript seek the embedded player instead of opening a new tab
- Keep the video player visible at all times while scrolling through content (sticky positioning)
- Maintain a clean, responsive layout

**Non-Goals:**
- Custom video player controls beyond what YouTube IFrame API provides
- Supporting non-YouTube video sources
- Backend changes — this is entirely a frontend enhancement
- Mobile-specific layout (will use a single-column fallback that still works)

## Decisions

### 1. YouTube IFrame Player API for embedding and seeking

**Choice:** Use the official YouTube IFrame Player API (`https://www.youtube.com/iframe_api`), loaded dynamically via a script tag.

**Why:** The IFrame API provides `player.seekTo(seconds)` which is exactly what we need for programmatic timestamp seeking. A simple `<iframe>` embed does not support seeking from outside the frame. The API is free, well-documented, and requires no npm dependencies.

**Alternatives considered:**
- Plain `<iframe>` with `src` updates: Would reload the player on every seek, causing flickering and buffering. Rejected.
- `react-youtube` npm package: Adds a dependency for a thin wrapper. The raw API is simple enough to integrate directly with a custom React hook. Rejected for simplicity.

### 2. Custom React hook `useYouTubePlayer` for player lifecycle

**Choice:** Create a `useYouTubePlayer(videoId)` hook that manages loading the IFrame API script, creating the player instance, and exposing a `seekTo(seconds)` function.

**Why:** Encapsulates all YouTube API interaction in one place. The hook loads the API script once (idempotent), creates the player when the container ref is available, and cleans up on unmount. Components only need to call `seekTo()`.

### 3. Two-column sticky layout for desktop

**Choice:** Use CSS `position: sticky` on the video player container within a two-column grid layout. The left column holds the sticky player, the right column holds the scrollable summary/transcript content.

**Why:** `position: sticky` is well-supported in modern browsers, requires no JavaScript for scroll handling, and degrades gracefully. On narrow viewports (< 768px), the layout collapses to a single column with the video sticky at the top.

**Alternatives considered:**
- `position: fixed`: Would take the player out of document flow, requiring manual offset calculations and causing overlap issues. Rejected.
- Intersection Observer for custom scroll behavior: Over-engineered for this use case. Rejected.

### 4. Callback prop on TimestampLink instead of `<a>` tags

**Choice:** Modify `TimestampLink` to accept an optional `onSeek` callback prop. When `onSeek` is provided, render a `<button>` that calls `onSeek(seconds)` instead of an `<a>` tag linking to YouTube. When `onSeek` is absent, fall back to the existing external link behavior.

**Why:** This is backward-compatible — `TimestampLink` still works as a link on pages without an embedded player (e.g., if the component is reused elsewhere). The video detail page passes `onSeek` wired to the player's `seekTo`.

## Risks / Trade-offs

- **YouTube API availability**: If the IFrame API script fails to load (network issue, ad blocker), the player won't render. **Mitigation:** Show a fallback message with a direct YouTube link when the player fails to initialize. The `TimestampLink` can also fall back to external links if `onSeek` is not provided.
- **Sticky layout on small screens**: A two-column layout doesn't work on narrow viewports. **Mitigation:** Use a responsive breakpoint (768px). On mobile, use a single column with the player sticky at the top (smaller height) so it remains visible without taking too much space.
- **Player load delay**: The YouTube IFrame API loads asynchronously. **Mitigation:** Show a loading placeholder in the player area until the `onReady` event fires.
