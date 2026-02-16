## ADDED Requirements

### Requirement: Read aloud summary and key points
The system SHALL provide a read-aloud feature that uses the browser's Web Speech Synthesis API to speak the summary overview and key points of a completed video sequentially.

#### Scenario: Start reading aloud
- **WHEN** the user clicks the read-aloud icon button on the video detail page of a completed video
- **THEN** the system begins speaking the summary overview text, followed by each key point text in order

#### Scenario: Pause reading
- **WHEN** the user clicks the pause button while speech is playing
- **THEN** the system pauses speech at the current position and displays a resume button

#### Scenario: Resume reading
- **WHEN** the user clicks the resume button while speech is paused
- **THEN** the system resumes speech from the paused position

#### Scenario: Stop reading
- **WHEN** the user clicks the stop button while speech is playing or paused
- **THEN** the system cancels all speech and resets the controls to the initial play state

#### Scenario: Speech completes naturally
- **WHEN** the system finishes speaking all key points (the last segment)
- **THEN** the controls reset to the initial play state

#### Scenario: Navigation cancels speech
- **WHEN** the user navigates away from the video detail page while speech is playing or paused
- **THEN** the system cancels all active speech

### Requirement: Read-aloud button visibility
The system SHALL only display the read-aloud button when the video is completed and a summary exists, and the browser supports speech synthesis.

#### Scenario: Button visible for completed video with summary
- **WHEN** the user views a completed video that has a summary
- **THEN** the read-aloud icon button is displayed in the meta/status line next to the status badge

#### Scenario: Button hidden for incomplete video
- **WHEN** the user views a video with status "queued", "processing", or "failed"
- **THEN** no read-aloud button is displayed

#### Scenario: Button hidden when speech synthesis unsupported
- **WHEN** the user's browser does not support the Web Speech Synthesis API
- **THEN** no read-aloud button is displayed

### Requirement: Text highlighting during read-aloud
The system SHALL optionally highlight the section of text currently being spoken, controlled by the `VITE_ENABLE_READING_HIGHLIGHT` feature flag.

#### Scenario: Highlighting enabled — summary being read
- **WHEN** the feature flag `VITE_ENABLE_READING_HIGHLIGHT` is set to `true` and the system is reading the summary overview
- **THEN** the summary overview element is visually highlighted

#### Scenario: Highlighting enabled — key point being read
- **WHEN** the feature flag is enabled and the system is reading a specific key point
- **THEN** that key point's list item is visually highlighted, and previous highlights are removed

#### Scenario: Highlighting disabled
- **WHEN** the feature flag is not set or set to `false`
- **THEN** no visual highlighting is applied during read-aloud, but speech still plays normally

#### Scenario: Highlight clears on stop
- **WHEN** the user stops reading or speech completes
- **THEN** all visual highlights are removed
