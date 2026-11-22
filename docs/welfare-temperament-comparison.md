# Welfare Assessment & Temperament Methods Comparison (CWA-41)

## Purpose
Compare established canine welfare assessment and temperament evaluation methods to ground the non-diagnostic behavioral observation model used in Companion Welfare AI.

## Comparative Matrix
| Method / Framework | Focus Area | Input & Protocol | Strengths | Limitations for Desktop Video Tool |
| --- | --- | --- | --- | --- |
| **C-BARQ (Canine Behavioral Assessment & Research Questionnaire)** | Breed/individual temperament & behavioral traits | Structured owner-completed questionnaire (100+ items across fear, aggression, separation, excitability) | Widely validated baseline for temperament context; easy to collect alongside video | Self-reported and static; does not capture frame-level temporal dynamics in short clips |
| **QBA (Qualitative Behavioral Assessment)** | Emotional expressivity & holistic welfare state | Trained observer rating expressive body language descriptors on visual analog scales | Captures whole-body demeanor (relaxed, tense, anxious, playful) from video | Subjective without standardized anchor definitions; requires rater calibration |
| **Ethogram-Based Behavioral Coding** | Observable posture, gait, and discrete events | Timestamped annotation of specific behaviors (pacing, lip-licking, yawning, tail/ear posture, resting) | Objective, reproducible, maps directly to video timestamps and pose/action classifiers | Time-consuming manually; requires clear non-diagnostic interpretation |
| **Pain & Acute Stress Scales (e.g., Glasgow CMPS-SF)** | Clinical pain and acute distress screening | Standardized physical/behavioral clinical scoring by professionals | High clinical validity for acute pain detection | Strictly diagnostic/clinical; inappropriate for automated owner-facing software |

## Synthesis & Design Decisions for Companion Welfare AI
1. **Ethogram-Inspired Observable Events (`BehaviorEvent`)**: The desktop system detects and logs timestamped, observable posture and movement patterns rather than diagnostic labels.
2. **Contextual Temperament Metadata (`C-BARQ` / Profile Context)**: Owner-provided profile and baseline temperament notes provide context without turning questionnaire scores into medical claims.
3. **Human-in-the-Loop Annotation (`is_manual`)**: Combining automated detections with manual timeline events preserves qualitative reviewer judgment without clinical overreach.
4. **Strict Non-Diagnostic Framing**: Clinical pain/diagnostic scales are excluded from automated outputs, reinforced by `NON_DIAGNOSTIC_NOTICE` in previews and exported reports.