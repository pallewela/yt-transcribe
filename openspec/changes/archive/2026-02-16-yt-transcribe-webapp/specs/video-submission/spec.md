## ADDED Requirements

### Requirement: Submit single YouTube URL
The system SHALL accept a single YouTube video URL and create a processing job for it.

#### Scenario: Valid YouTube URL submitted
- **WHEN** the user submits a valid YouTube video URL (e.g., `https://www.youtube.com/watch?v=...` or `https://youtu.be/...`)
- **THEN** the system creates a new video record with status "queued" and returns the video ID and status

#### Scenario: Invalid URL submitted
- **WHEN** the user submits a URL that is not a valid YouTube video URL
- **THEN** the system rejects the submission with a validation error indicating the URL is not a recognized YouTube format

#### Scenario: Duplicate URL submitted
- **WHEN** the user submits a YouTube URL that has already been submitted
- **THEN** the system returns the existing video record and its current status instead of creating a duplicate

### Requirement: Submit batch of YouTube URLs
The system SHALL accept multiple YouTube video URLs in a single request and create processing jobs for each.

#### Scenario: Multiple valid URLs submitted
- **WHEN** the user submits a list of valid YouTube URLs
- **THEN** the system creates a video record for each URL with status "queued" and returns a list of video IDs and statuses

#### Scenario: Mixed valid and invalid URLs in batch
- **WHEN** the user submits a batch containing both valid and invalid YouTube URLs
- **THEN** the system creates records for the valid URLs and returns validation errors for the invalid ones, without rejecting the entire batch

### Requirement: YouTube URL validation
The system SHALL validate YouTube URLs against known YouTube URL patterns.

#### Scenario: Standard watch URL accepted
- **WHEN** a URL matching `https://www.youtube.com/watch?v=VIDEO_ID` is submitted
- **THEN** the system accepts the URL and extracts the video ID

#### Scenario: Short URL accepted
- **WHEN** a URL matching `https://youtu.be/VIDEO_ID` is submitted
- **THEN** the system accepts the URL and extracts the video ID

#### Scenario: Non-YouTube URL rejected
- **WHEN** a URL from a non-YouTube domain is submitted
- **THEN** the system rejects the URL with a clear error message

### Requirement: Fetch video metadata on submission
The system SHALL retrieve the video title and duration from YouTube when a URL is submitted.

#### Scenario: Metadata successfully retrieved
- **WHEN** a valid YouTube URL is submitted and the video is accessible
- **THEN** the system stores the video title and duration alongside the URL

#### Scenario: Video unavailable
- **WHEN** a YouTube URL points to a private, deleted, or unavailable video
- **THEN** the system creates the record with status "failed" and an error message indicating the video is unavailable
