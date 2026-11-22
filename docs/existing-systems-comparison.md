# Existing Companion Animal Monitoring Systems Comparison (CWA-7)

## Purpose
Evaluate existing commercial and research companion animal monitoring systems across data modality, privacy/storage architecture, interpretability, and diagnostic framing to position Companion Welfare AI.

## Comparative Matrix
| System / Category | Primary Modality | Storage & Processing | Behavioral Granularity | Key Limitations |
| --- | --- | --- | --- | --- |
| **Smart Collars (e.g., Fi, Whistle, PetPace)** | Accelerometer / GPS / biometric sensors | Proprietary cloud servers + subscription app | Coarse activity levels, sleep/rest duration, location, basic step counts | Requires wearable hardware; opaque proprietary scores; cloud lock-in; no video context |
| **Cloud Pet Cameras (e.g., Furbo, Petcube)** | Fixed indoor RGB camera + audio | Cloud video streaming & vendor servers | Bark alerts, motion alerts, basic treat tossing | Continuous cloud upload raises privacy concerns; lacks structured ethogram/posture timeline |
| **General Pose / Action Research Pipelines (e.g., DeepLabCut, SLEAP)** | High-resolution lab/home video | Local GPU/workstation scripts | Fine-grained anatomical keypoints and kinematic trajectories | High technical barrier for dog owners; no built-in consent workflow, session DB, or non-diagnostic report export |
| **Companion Welfare AI (Our Desktop System)** | Local user-selected video files | **100% local SQLite + local file store** (`consent_given` gated) | Timestamped observable behavior events + manual reviewer annotations (`is_manual`) | Offline batch/clip review rather than 24/7 live hardware streaming |

## Key Differentiators of Companion Welfare AI
1. **Local-First Privacy & Explicit Consent**: Unlike cloud cameras and collar ecosystems, video processing and SQLite persistence happen locally on the user's machine only after explicit consent (`SYS-01`, `SYS-02`).
2. **Hardware-Free Video Review**: Works with standard recorded video clips without requiring proprietary collars or specialized lab setups.
3. **Human-in-the-Loop Timeline**: Combines automated event detection with timestamped manual annotations and frame scrubbing (`SYS-03`..`SYS-05`).
4. **Explicit Non-Diagnostic Guardrails**: Avoids opaque "health score" claims by enforcing `NON_DIAGNOSTIC_NOTICE` across previews and exported Markdown reports (`SYS-06`).