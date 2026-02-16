### Requirement: Embed YouTube video player on detail page
The system SHALL embed a YouTube video player on the video detail page for completed videos using the YouTube IFrame Player API.

#### Scenario: Player renders for completed video
- **WHEN** the user navigates to the detail page of a video with status "completed"
- **THEN** the system displays an embedded YouTube player loaded with that video

#### Scenario: Player not rendered for incomplete video
- **WHEN** the user navigates to the detail page of a video with status "queued" or "processing"
- **THEN** no embedded player is displayed

#### Scenario: Player API fails to load
- **WHEN** the YouTube IFrame API script fails to load (network error, blocked by extension)
- **THEN** the system displays a fallback message with a direct link to the YouTube video

### Requirement: Programmatic seeking via timestamps
The system SHALL seek the embedded player to a specific time when a timestamp is clicked in the key points or transcript sections.

#### Scenario: Click key point timestamp
- **WHEN** the user clicks a timestamp in the key points section
- **THEN** the embedded player seeks to the corresponding time and begins playback

#### Scenario: Click transcript timestamp
- **WHEN** the user clicks a timestamp in the transcript section
- **THEN** the embedded player seeks to the corresponding time and begins playback

### Requirement: Inline video player layout
The system SHALL display the embedded video player inline within the single-column page flow, positioned below the status line and above the summary section. The player is no longer sticky or in a side column.

#### Scenario: Player positioned inline on desktop
- **WHEN** the user views the detail page of a completed video on any viewport width
- **THEN** the embedded YouTube player is displayed in normal document flow below the transcription status and above the summary, without sticky positioning

#### Scenario: Player scales on narrow viewports
- **WHEN** the user views the detail page on a narrow viewport
- **THEN** the player scales to the full width of the container while maintaining its 16:9 aspect ratio

### Requirement: Player loading state
The system SHALL display a loading placeholder while the YouTube player is initializing.

#### Scenario: Player loading indicator
- **WHEN** the embedded player is loading (API script loading or player initializing)
- **THEN** the system displays a placeholder in the player area indicating the video is loading
