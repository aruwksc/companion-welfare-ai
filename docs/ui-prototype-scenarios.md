# UI Prototype & Scenario Walkthrough S1–S4 (CWA-25)

## Purpose
Document the interactive prototype screen architecture and scenario testing (S1–S4) that guided the PySide6 desktop interface (`app/ui/main_window.py`).

## Prototype Screen Layout & Navigation
- **Left Panel — Dog Profile & Consent Setup**: Dog name, breed, age, baseline temperament/notes, and explicit owner consent checkbox (`consent_given`) gating all media import and analysis actions.
- **Center Panel — Video Session & Timeline Review**: Local video import selector, video preview canvas with frame scrubber (`QSlider`), playback controls, and detected/manual behavior event list.
- **Right Panel — Manual Annotation & Report Export**: Manual timestamped event entry (`event_type`, `notes`), non-diagnostic disclaimer banner (`NON_DIAGNOSTIC_NOTICE`), live Markdown report preview, and export action.

## Prototype Scenario Testing (S1–S4)
| Scenario | Goal | Prototype Flow & Verification | Status |
| --- | --- | --- | --- |
| **S1: Consent-Gated Onboarding** | Prevent unconsented video import/analysis | Verified that import/analysis controls remain blocked until profile is saved with explicit owner consent enabled (`SYS-01`, `SYS-02`). | **Verified** |
| **S2: Local Video Import & Analysis** | Run offline behavioral observation on a local video | Verified local file selection, progress feedback during offline frame analysis, and automatic population of timestamped events (`SYS-03`). | **Verified** |
| **S3: Timeline Scrubbing & Manual Event Entry** | Inspect specific video moments and add reviewer notes | Verified clicking an event jumps the video frame preview to the corresponding timestamp and allows adding manual observations (`SYS-05`). | **Verified** |
| **S4: Non-Diagnostic Report Review & Export** | Generate a safe, shareable summary | Verified prominent non-diagnostic disclaimer in UI preview and Markdown export without clinical/diagnostic claims (`SYS-06`). | **Verified** |

## Key Usability Takeaways Applied to Desktop UI
- Kept single-window three-column layout so reviewers do not lose timeline context while writing annotations or reviewing reports.
- Surfaced non-diagnostic framing directly above the report preview rather than hiding it in a secondary modal.