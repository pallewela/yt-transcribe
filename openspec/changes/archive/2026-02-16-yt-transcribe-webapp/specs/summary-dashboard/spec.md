## ADDED Requirements

### Requirement: List all submitted videos
The system SHALL display a list of all submitted videos with their current status.

#### Scenario: Dashboard shows all videos
- **WHEN** the user navigates to the dashboard
- **THEN** the system displays a list of all submitted videos showing: title, URL, status (queued/processing/completed/failed), and submission date

#### Scenario: Empty state
- **WHEN** the user navigates to the dashboard and no videos have been submitted
- **THEN** the system displays a message encouraging the user to submit their first video

### Requirement: View video summary with clickable timestamps
The system SHALL allow the user to view the full summary for a completed video, with key points linked to the corresponding moments in the YouTube video.

#### Scenario: Summary displayed for completed video
- **WHEN** the user selects a video with status "completed"
- **THEN** the system displays the video title, the generated summary overview, key points with clickable timestamp links, and the full transcript

#### Scenario: Clicking a timestamp in the summary
- **WHEN** the user clicks a timestamp link on a summary key point
- **THEN** the system opens the YouTube video in a new tab at the corresponding time (using the `?t=` URL parameter)

#### Scenario: Summary not available for incomplete video
- **WHEN** the user selects a video that is still "queued" or "processing"
- **THEN** the system shows the current processing status and does not display a summary

### Requirement: Display timestamped transcript
The system SHALL display the full transcript with visible timestamps that are also clickable.

#### Scenario: Transcript displayed with timestamps
- **WHEN** the user views the transcript section of a completed video
- **THEN** each transcript segment is displayed with its timestamp, and clicking the timestamp opens the YouTube video at that point in a new tab

### Requirement: Filter videos by status
The system SHALL allow the user to filter the video list by processing status.

#### Scenario: Filter by completed
- **WHEN** the user filters by "completed" status
- **THEN** only videos with completed summaries are displayed

#### Scenario: Filter by failed
- **WHEN** the user filters by "failed" status
- **THEN** only failed videos are displayed, each showing its error message

### Requirement: Delete a video and its data
The system SHALL allow the user to delete a submitted video along with its transcript and summary.

#### Scenario: Successful deletion
- **WHEN** the user deletes a video
- **THEN** the video record, transcript, and summary are permanently removed from the database

### Requirement: Submit videos from the dashboard
The system SHALL provide an input area on the dashboard for submitting new YouTube URLs.

#### Scenario: Submit from dashboard
- **WHEN** the user enters one or more YouTube URLs in the submission area and submits
- **THEN** the system validates and queues the URLs for processing and updates the video list to show the new entries with "queued" status

### Requirement: Auto-refresh dashboard status
The system SHALL periodically refresh the video list to reflect updated processing statuses.

#### Scenario: Status updates without manual refresh
- **WHEN** a video's status changes from "processing" to "completed"
- **THEN** the dashboard reflects the updated status within a reasonable polling interval without requiring a manual page refresh
