## ADDED Requirements

### Requirement: Generate summary from transcript
The system SHALL generate a concise summary from a video's transcript using an LLM.

#### Scenario: Successful summarization
- **WHEN** a video's timestamped transcript is available
- **THEN** the system sends the timestamped transcript to the LLM API with instructions to produce a summary with timestamp-anchored key points, and stores the result in the database

#### Scenario: Summarization fails
- **WHEN** the LLM API returns an error during summarization
- **THEN** the system marks the job as "failed" with the error details, but the transcript is preserved

### Requirement: Summary structure with timestamp anchors
The system SHALL produce summaries where each key point is anchored to a specific timestamp from the transcript.

#### Scenario: Summary content format
- **WHEN** a summary is generated
- **THEN** the summary includes a 2-3 sentence overview followed by a list of key points, where each key point includes a timestamp (in seconds) referencing the relevant moment in the video

#### Scenario: Summary stored as structured data
- **WHEN** a summary is generated
- **THEN** the summary is stored as JSON containing an `overview` string and a `key_points` array, where each key point has `timestamp` (seconds), `text` (the point), and optionally `end_timestamp` (seconds)

### Requirement: Handle long transcripts
The system SHALL handle transcripts that exceed the LLM's context window while preserving timestamp information.

#### Scenario: Transcript within context limit
- **WHEN** the transcript fits within the LLM's context window
- **THEN** the system sends the entire timestamped transcript in a single request

#### Scenario: Transcript exceeds context limit
- **WHEN** the transcript exceeds the LLM's context window
- **THEN** the system chunks the transcript preserving segment timestamps, summarizes each chunk with timestamp anchors, and produces a final combined summary where all timestamps reference the original video timeline

### Requirement: Mark video as completed after summarization
The system SHALL update the video status to "completed" once summarization finishes successfully.

#### Scenario: Status updated to completed
- **WHEN** the summary has been generated and stored
- **THEN** the video record status changes to "completed" and includes a completion timestamp
