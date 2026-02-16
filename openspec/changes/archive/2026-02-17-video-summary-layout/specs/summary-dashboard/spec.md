## MODIFIED Requirements

### Requirement: View video summary with clickable timestamps
The system SHALL allow the user to view the full summary for a completed video, with the page laid out in a single-column, top-down flow: video topic (linked to YouTube), transcription status and transcript source, embedded player, summary overview, and key points with clickable timestamp links.

#### Scenario: Summary displayed for completed video
- **WHEN** the user selects a video with status "completed"
- **THEN** the system displays the page in the following top-to-bottom order: (1) the video topic as a clickable heading that links to the YouTube video, (2) the transcription status badge and transcript source, (3) the embedded YouTube player, (4) the summary overview, (5) key points with clickable timestamp links, and (6) the full transcript toggle

#### Scenario: Video topic links to YouTube
- **WHEN** the user clicks the video topic heading on the detail page
- **THEN** the YouTube video opens in a new browser tab

#### Scenario: Key points are independently scrollable
- **WHEN** the key points section contains more items than fit in its visible area
- **THEN** the key points section scrolls independently without scrolling the rest of the page

#### Scenario: Clicking a timestamp in the summary
- **WHEN** the user clicks a timestamp link on a summary key point
- **THEN** the embedded YouTube player seeks to the corresponding time and begins playback

#### Scenario: Summary not available for incomplete video
- **WHEN** the user selects a video that is still "queued" or "processing"
- **THEN** the system shows the video topic, transcription status, and a processing message — no player, summary, or key points are displayed
