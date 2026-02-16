## MODIFIED Requirements

### Requirement: Sticky video player layout
The system SHALL display the embedded video player inline within the single-column page flow, positioned below the status line and above the summary section. The player is no longer sticky or in a side column.

#### Scenario: Player positioned inline on desktop
- **WHEN** the user views the detail page of a completed video on any viewport width
- **THEN** the embedded YouTube player is displayed in normal document flow below the transcription status and above the summary, without sticky positioning

#### Scenario: Player scales on narrow viewports
- **WHEN** the user views the detail page on a narrow viewport
- **THEN** the player scales to the full width of the container while maintaining its 16:9 aspect ratio

## REMOVED Requirements

### Requirement: Sticky video player layout
**Reason**: The two-column sticky layout (player pinned left on desktop, sticky-top on mobile) is replaced by a single-column inline layout per the video-summary-layout change. The player now sits in normal document flow.
**Migration**: No migration needed. The player renders in the same position within the new single-column flow. All seeking and fallback functionality is preserved.
