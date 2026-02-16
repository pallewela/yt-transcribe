## ADDED Requirements

### Requirement: Fetch YouTube captions as preferred transcript source
The system SHALL attempt to retrieve existing YouTube captions/subtitles before falling back to audio-based transcription.

#### Scenario: Captions available
- **WHEN** a video job moves to "processing" status and the video has existing captions (auto-generated or manual)
- **THEN** the system fetches the caption text with per-segment timestamps and uses it as the transcript, skipping audio download and Whisper entirely

#### Scenario: No captions available
- **WHEN** a video job moves to "processing" status and the video has no available captions
- **THEN** the system falls back to the audio download and Whisper transcription path

#### Scenario: Caption fetch fails
- **WHEN** the caption retrieval attempt fails (e.g., network error)
- **THEN** the system falls back to the audio download and Whisper transcription path rather than marking the job as failed

### Requirement: Record transcript source
The system SHALL record whether the transcript was obtained from YouTube captions or Whisper transcription.

#### Scenario: Transcript source stored
- **WHEN** a transcript is obtained from either source
- **THEN** the video record includes a field indicating the source ("youtube_captions" or "whisper")

### Requirement: Download audio from YouTube video (fallback)
The system SHALL download the audio track from a YouTube video when captions are not available.

#### Scenario: Audio successfully downloaded
- **WHEN** no YouTube captions are available for a video
- **THEN** the system downloads the audio track using yt-dlp and stores it as a temporary file

#### Scenario: Download fails
- **WHEN** the audio download fails (network error, rate limiting, video removed)
- **THEN** the system marks the job as "failed" with a descriptive error message and does not proceed to transcription

### Requirement: Transcribe audio to text via Whisper (fallback)
The system SHALL convert downloaded audio to text using the Whisper API when YouTube captions are unavailable.

#### Scenario: Successful transcription
- **WHEN** the audio file has been downloaded successfully
- **THEN** the system sends the audio to the Whisper API using verbose JSON response format to obtain segment-level timestamps, and stores the resulting timestamped transcript in the database

#### Scenario: Transcription fails
- **WHEN** the transcription API returns an error
- **THEN** the system marks the job as "failed" with the error details and cleans up the temporary audio file

#### Scenario: Long audio handling
- **WHEN** the audio file exceeds the API's size limit (25MB for Whisper)
- **THEN** the system splits the audio into chunks, transcribes each chunk, and concatenates the results

### Requirement: Clean up temporary audio files
The system SHALL delete temporary audio files after transcription completes or fails.

#### Scenario: Cleanup after successful transcription
- **WHEN** transcription completes successfully
- **THEN** the temporary audio file is deleted from disk

#### Scenario: Cleanup after failed transcription
- **WHEN** transcription fails
- **THEN** the temporary audio file is deleted from disk

### Requirement: Store transcript with timestamps
The system SHALL persist the transcript as timestamped segments in the database linked to the video record.

#### Scenario: Timestamped transcript stored
- **WHEN** transcription completes successfully (from either captions or Whisper)
- **THEN** the transcript is saved as a JSON array of segments, each containing a start time (in seconds) and text, associated with the video record

#### Scenario: Plain text transcript derived
- **WHEN** the timestamped transcript is stored
- **THEN** a plain-text version of the full transcript (segments concatenated) is also stored for display and summarization input
