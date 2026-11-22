# Interview Evidence Synthesis & Hypothesis Assessment (CWA-21)

## Purpose
Synthesize qualitative findings from stakeholder/owner interviews and evaluate project hypotheses to inform requirements consolidation and desktop workflow priorities.

## Key Interview Takeaways
1. **Explicit Consent & Local Privacy First**: Dog owners expect clear consent tracking and prefer local processing/storage without unconsented external uploads.
2. **Observable Behaviour vs. Medical Diagnosis**: Users and reviewers need transparent, non-diagnostic observations (movement/posture patterns and uncertainty) rather than veterinary medical claims.
3. **Practical Review & Manual Annotation**: Reviewing video frames with timeline jump and adding manual notes helps bridge automated detections and real-world context.
4. **Clear, Portable Summary Export**: Having a readable report format with explicit non-diagnostic framing supports sharing notes with trainers or caregivers.

## Hypothesis Assessment Summary
| ID | Hypothesis | Status | Evidence & Impact on System |
| --- | --- | --- | --- |
| H-01 | Users want a single-click workflow with explicit consent before video analysis. | **Supported** | Consent gate and local video import/analysis flow are core to the desktop workflow. |
| H-02 | Automated behaviour detections alone cover all user review needs without manual input. | **Refuted / Partially Refuted** | Manual timeline annotations (`is_manual`) are needed alongside model events to capture context. |
| H-03 | Outputs presented as clinical/diagnostic conclusions are preferred by dog owners. | **Refuted** | Non-diagnostic framing and uncertainty disclosure (`NON_DIAGNOSTIC_NOTICE`) are required to prevent misinterpretation. |
| H-04 | Local SQLite storage and Markdown report export satisfy offline review needs. | **Supported** | SQLite persistence (`WelfareRepository`) and Markdown report export cover offline session tracking. |

## Follow-Up for Requirements & Implementation
- Keep non-diagnostic notice prominent in UI preview and exported reports.
- Preserve both automated model events and manual annotations in stored sessions and reports.
- Use these validated findings when consolidating requirements and preparing final release notes.