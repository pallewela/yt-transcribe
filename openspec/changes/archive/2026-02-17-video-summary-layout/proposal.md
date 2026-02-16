## Why

The current video detail page uses a two-column layout (sticky player on the left, scrollable content on the right) which doesn't present information in an ideal reading flow. The video topic isn't prominently positioned, there's no direct link to the YouTube video from the title, and the key points section scrolls with the entire page rather than being independently scrollable. Reorganizing to a single-column, top-down layout improves readability, puts the most important context (topic, status) first, and gives key points their own scroll region so users can browse them without losing their place on the page.

## What Changes

- **Reorder page layout to single-column, top-down flow**: Replace the current two-column (sticky player left, content right) layout with a vertical stack: topic → status → player → summary → key points.
- **Video topic as linked heading at top**: Move the video title/topic to the very top of the page and make it a clickable link that opens the YouTube video in a new tab.
- **Status and transcript source below topic**: Move the transcription status badge and transcript source indicator directly below the topic heading, before the player.
- **Embedded player below status**: The embedded YouTube player moves below the status line instead of being in a sticky left column.
- **Summary below player**: The summary overview section renders below the embedded player.
- **Key points with independent scrolling**: The key points section renders below the summary inside a scroll container with a fixed max-height, so scrolling key points does not scroll the rest of the page.
- **Remove sticky two-column player layout**: The existing sticky/side-by-side desktop layout and the sticky-top mobile layout for the player are removed.

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `summary-dashboard`: The "View video summary" requirement changes — the detail page layout order is reorganized and the video title becomes a clickable link to the YouTube video.
- `embedded-player`: The "Sticky video player layout" requirement is replaced — the player is no longer sticky or in a side column; it sits inline in the single-column flow below the status line.

## Impact

- **Frontend component**: `frontend/src/pages/VideoDetail.jsx` — major layout restructure (element ordering, removal of two-column grid, addition of scroll container for key points).
- **Frontend styles**: `frontend/src/pages/VideoDetail.module.css` — rewrite of layout-related styles (remove sticky/grid classes, add scroll container styles).
- **No backend changes**: API responses and data model remain unchanged.
- **No dependency changes**: No new libraries needed.
- **Responsive behavior**: The sticky player responsive breakpoint logic (768px) is removed since the layout is now single-column at all widths.
