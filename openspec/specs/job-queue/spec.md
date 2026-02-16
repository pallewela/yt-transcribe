### Requirement: Enqueue video for processing
The system SHALL add submitted videos to a processing queue with an initial status of "queued".

#### Scenario: Video enqueued after submission
- **WHEN** a video URL passes validation and a record is created
- **THEN** the video is added to the job queue with status "queued"

### Requirement: Process jobs sequentially from the queue
The system SHALL pick up queued jobs and process them through the transcription and summarization pipeline.

#### Scenario: Next job picked up
- **WHEN** the worker is idle and there are queued jobs
- **THEN** the system picks the oldest queued job, changes its status to "processing", and begins the transcription pipeline

#### Scenario: No jobs in queue
- **WHEN** the worker checks for jobs and the queue is empty
- **THEN** the worker waits and polls again after a configurable interval

### Requirement: Track job status transitions
The system SHALL maintain a status field for each video that reflects its current processing stage.

#### Scenario: Status progression for successful processing
- **WHEN** a video is processed successfully through the full pipeline
- **THEN** its status transitions through: "queued" → "processing" → "completed"

#### Scenario: Status on failure
- **WHEN** any step in the pipeline fails
- **THEN** the video status changes to "failed" with an error message describing what went wrong

### Requirement: Retry failed jobs
The system SHALL support retrying failed jobs up to a configurable maximum number of attempts.

#### Scenario: Automatic retry on transient failure
- **WHEN** a job fails and has not reached the maximum retry count
- **THEN** the system re-queues the job with an incremented attempt counter after a delay

#### Scenario: Permanent failure after max retries
- **WHEN** a job has failed and reached the maximum retry count
- **THEN** the system marks the job as permanently "failed" and does not retry

### Requirement: Background worker runs alongside the web server
The system SHALL run the job processing worker as a background task within the same application process.

#### Scenario: Worker starts with the application
- **WHEN** the application starts
- **THEN** the background worker begins polling for queued jobs automatically

#### Scenario: Worker does not block the web server
- **WHEN** jobs are being processed
- **THEN** the web API remains responsive and can accept new submissions and serve dashboard requests
