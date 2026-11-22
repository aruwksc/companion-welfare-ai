# Use Case Diagram — Companion Welfare AI (CWA-23)

## Actors
- **Dog Owner / Reviewer**: Creates dog profiles, records or revokes local processing consent, imports local videos, runs offline analysis, reviews frames and event timelines, adds manual annotations, and previews/exports Markdown reports.
- **Local Vision / Analysis Engine (`PosePort` / `BehaviourPort`)**: Processes imported local video frames offline to detect observable movement/posture patterns with confidence scores.
- **Local Storage (`WelfareRepository` & Local File System)**: Persists profiles, consent records, video metadata/files, sessions, events, and exported reports locally in SQLite and local directories.

## Diagram

flowchart LR
    Owner["Dog Owner / Reviewer"]
    Vision["Local Vision Engine<br/>(PosePort / BehaviourPort)"]
    Storage["Local SQLite & File Store<br/>(WelfareRepository)"]

    subgraph DesktopApp["Companion Welfare AI Desktop App"]
        UC1["UC-01: Create & Select Dog Profile"]
        UC2["UC-02: Record / Update Owner Consent"]
        UC3["UC-03: Import Local Video"]
        UC4["UC-04: Run Offline Behaviour Analysis"]
        UC5["UC-05: Scrub Video Frames & Review Timeline"]
        UC6["UC-06: Add Manual Event Annotation"]
        UC7["UC-07: Preview & Export Report<br/>(with Non-Diagnostic Notice)"]
    end

    Owner --> UC1
    Owner --> UC2
    Owner --> UC3
    Owner --> UC4
    Owner --> UC5
    Owner --> UC6
    Owner --> UC7

    UC3 -. "<<include>>" .-> UC2
    UC4 -. "<<include>>" .-> UC2
    UC4 --> Vision
    UC6 -. "<<extend>>" .-> UC5

    UC1 --> Storage
    UC2 --> Storage
    UC3 --> Storage
    UC4 --> Storage
    UC5 --> Storage
    UC6 --> Storage
    UC7 --> Storage

## Core Scenarios Summary
1. **Profile & Consent (`UC-01`, `UC-02`)**: Manage dog profiles and explicit owner consent state prior to video import and local analysis.
2. **Local Video Import & Offline Analysis (`UC-03`, `UC-04`)**: Import local video files into local storage and run offline analysis when active owner consent is granted.
3. **Timeline Review, Manual Annotation & Report Export (`UC-05`, `UC-06`, `UC-07`)**: Scrub video frames, jump to events from the timeline table, log manual observations, and export reports accompanied by the non-diagnostic notice.