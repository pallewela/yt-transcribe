## 1. Restructure JSX layout in VideoDetail

- [x] 1.1 Move the video title `<h1>` to the top of the page (after the back link) and wrap it in an `<a>` tag linking to `https://www.youtube.com/watch?v={video_id}` with `target="_blank"` and `rel="noopener noreferrer"`
- [x] 1.2 Move the status badge and transcript source `<div className={styles.meta}>` directly below the title, before the player
- [x] 1.3 Move the embedded player block below the meta/status section (remove it from the left column wrapper)
- [x] 1.4 Remove the two-column `<div className={styles.twoColumn}>` wrapper and `playerColumn`/`contentColumn` containers — render all elements in a single vertical flow
- [x] 1.5 Move the summary overview section below the player
- [x] 1.6 Extract key points into their own section below the summary, wrapped in a scroll container `<div>` with a `keyPointsScroll` CSS class
- [x] 1.7 Keep error, pending, and transcript sections below key points in the existing order

## 2. Update CSS styles

- [x] 2.1 Remove `.twoColumn` grid layout styles
- [x] 2.2 Remove `.playerColumn` and `.playerSticky` sticky positioning styles
- [x] 2.3 Remove `.contentColumn` styles
- [x] 2.4 Remove the `@media (max-width: 768px)` responsive block for the old two-column layout
- [x] 2.5 Add `.titleLink` styles for the linked heading (inherit font styles, appropriate hover state)
- [x] 2.6 Add `.keyPointsScroll` styles with `max-height: 400px` and `overflow-y: auto` for independent key points scrolling
- [x] 2.7 Constrain the player width with a `max-width` so it doesn't stretch too wide on large screens

## 3. Verify behavior

- [x] 3.1 Verify the title link opens the YouTube video in a new tab
- [x] 3.2 Verify status badge and transcript source display below the title
- [x] 3.3 Verify the embedded player renders below the status line
- [x] 3.4 Verify the summary renders below the player
- [x] 3.5 Verify key points scroll independently without scrolling the whole page
- [x] 3.6 Verify timestamp seeking still works from key points and transcript
- [x] 3.7 Verify fallback state (player error) still shows correctly
- [x] 3.8 Verify queued/processing/failed states display correctly with the new layout
