## Context

The video detail page (`/video/:id`) currently uses a two-column grid layout: a sticky YouTube player on the left and a scrollable content column on the right containing the title, status, summary, key points, and transcript. On mobile (<768px), it collapses to a single column with the player sticky at the top.

The proposal calls for replacing this with a single-column, top-down layout that reorders elements to: topic (linked) → status/source → embedded player → summary → key points (scrollable). This change is purely frontend — no backend or API modifications are needed.

Key files:
- `frontend/src/pages/VideoDetail.jsx` — component structure and render order
- `frontend/src/pages/VideoDetail.module.css` — layout, sticky, and grid styles

## Goals / Non-Goals

**Goals:**
- Reorganize the detail page into a clear, top-down single-column reading flow
- Make the video title a clickable link to the YouTube video (opens new tab)
- Place status and transcript source prominently below the title, before the player
- Give the key points section its own scroll container so browsing key points doesn't scroll the page
- Maintain all existing functionality (timestamp seeking, player fallback, transcript toggle, error/pending states)

**Non-Goals:**
- Redesigning the dashboard or any page other than the video detail page
- Changing the player implementation, API, or the `useYouTubePlayer` hook
- Modifying the backend API response shape or data model
- Adding new features (e.g., search, bookmarks, share links)

## Decisions

### 1. Single-column layout replaces two-column grid

**Decision**: Remove the CSS Grid two-column layout (`twoColumn`, `playerColumn`, `contentColumn`) and render all elements in a single vertical stack.

**Rationale**: The user's requirements specify a strict top-to-bottom order (topic → status → player → summary → key points). A single column naturally matches this flow at all viewport widths, eliminating the need for responsive breakpoint logic.

**Alternative considered**: Keep two columns but swap content (metadata on left, player on right). Rejected because the requirements explicitly call for a vertical, sequential layout.

### 2. Title as external link using an anchor tag

**Decision**: Wrap the `<h1>` title text in an `<a>` element with `href` pointing to the YouTube video URL (`https://www.youtube.com/watch?v={video_id}`), `target="_blank"`, and `rel="noopener noreferrer"`.

**Rationale**: This is the simplest implementation. Using a standard anchor tag provides native browser behavior (open in new tab, right-click context menu, accessibility). The `video_id` is already available in the video data.

**Alternative considered**: A button with `window.open()`. Rejected because an anchor tag is semantically correct for navigation and more accessible.

### 3. Key points scroll container with max-height

**Decision**: Wrap the key points `<ul>` in a container with `max-height: 400px` and `overflow-y: auto`. This gives it an independent scroll region.

**Rationale**: A fixed max-height ensures the key points section doesn't push the rest of the page content far down when there are many key points. 400px provides enough visible area for ~5-6 key points while keeping the summary and player visible above. The exact value can be tuned.

**Alternative considered**: Using `flex: 1` with `overflow` in a full-height layout. Rejected because it would force the entire page into a non-scrolling viewport-height layout, which would constrain the summary and player sections unnecessarily.

### 4. Remove all sticky positioning

**Decision**: Remove `.playerSticky` sticky positioning and the mobile sticky override. The player sits in normal document flow.

**Rationale**: With the new layout, the player is positioned between status and summary — it scrolls with the page like any other element. Sticky behavior is no longer needed since the key points have their own scroll container.

### 5. Player rendering for all statuses

**Decision**: Keep existing behavior — the player only renders when `status === 'completed'`. For queued/processing/failed states, only the title, status, and relevant message are shown (no player).

**Rationale**: No change from current behavior. The requirements focus on layout reordering, not changing when elements appear.

## Risks / Trade-offs

- **Long summaries push key points below the fold** → Acceptable trade-off; the linear reading order (summary then key points) matches the user's specification. Users scroll naturally to reach key points.
- **Fixed max-height for key points may not suit all screen sizes** → Mitigation: Use a reasonable default (400px) that works for most viewports. Can be refined later with viewport-relative units if needed.
- **Losing sticky player means users can't see the video while reading key points** → This is an intentional design choice per the requirements. Users can scroll up to the player, and timestamp links still seek the player.
- **No responsive breakpoint needed** → The single-column layout works at all widths. The player's `aspect-ratio: 16/9` and `max-width: 100%` ensure it scales down on narrow viewports.
