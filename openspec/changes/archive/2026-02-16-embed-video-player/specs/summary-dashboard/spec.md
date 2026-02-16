## MODIFIED Requirements

### Requirement: View video summary with clickable timestamps
The system SHALL allow the user to view the full summary for a completed video, with key points linked to the corresponding moments in the embedded YouTube player.

#### Scenario: Summary displayed for completed video
- **WHEN** the user selects a video with status "completed"
- **THEN** the system displays the video title, the generated summary overview, key points with clickable timestamp links, and the full transcript

#### Scenario: Clicking a timestamp in the summary
- **WHEN** the user clicks a timestamp link on a summary key point
- **THEN** the embedded YouTube player seeks to the corresponding time and begins playback

#### Scenario: Summary not available for incomplete video
- **WHEN** the user selects a video that is still "queued" or "processing"
- **THEN** the system shows the current processing status and does not display a summary

### Requirement: Display timestamped transcript
The system SHALL display the full transcript with visible timestamps that seek the embedded player when clicked.

#### Scenario: Transcript displayed with timestamps
- **WHEN** the user views the transcript section of a completed video
- **THEN** each transcript segment is displayed with its timestamp, and clicking the timestamp seeks the embedded YouTube player to that point
