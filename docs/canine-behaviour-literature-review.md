# Literature Review: Canine Behaviour & Welfare Signals (CWA-12)

## Purpose
Synthesize foundational concepts from canine ethology and animal welfare literature to support consistent behavioral observation, manual annotation, and non-diagnostic reporting in Companion Welfare AI.

## Key Themes in Canine Behaviour Literature
1. **Observable Body Language & Posture Context**: Canine behavior is multimodal—posture, ear and tail position, head orientation, gait, and rest/activity transitions must be interpreted together and within environmental context rather than in isolation.
2. **Stress, Arousal, and Calming/Displacement Signals**: Behaviors such as lip-licking, yawning, nose-licking, pacing, scanning, or sudden freeze/withdrawal can reflect arousal, uncertainty, or mild stress, but overlap with normal physiological states (e.g., fatigue or environment transition).
3. **Activity & Rest Patterns**: Changes in rest/sleep routines, restlessness, or movement cadence are useful indicators to track over time, while remaining non-specific without veterinary assessment.
4. **Limits of Automated & Single-Frame Inference**: Automated or frame-level visual cues indicate *observable patterns* and *uncertainty*, not clinical diagnoses or emotional certainty.

## How This Informs Companion Welfare AI
- **Timestamped Events + Manual Context**: Detected events (`BehaviorEvent`) mark time intervals for review, while manual annotations (`is_manual`) let owners/reviewers record situational context.
- **No Diagnostic Claims**: All previews and exported reports enforce `NON_DIAGNOSTIC_NOTICE` so observable behavioral patterns are not mistaken for veterinary diagnosis.