# Dog Owner Recruitment Protocol for Video & C-BARQ Dataset (CWA-38)

## Purpose
Define participant eligibility, informed consent rules, and anonymized intake procedures for collecting dog behavioral video clips paired with C-BARQ temperament questionnaires.

## Eligibility & Inclusion Criteria
- Adult dog owners/caretakers (18+) willing to provide explicit written/digital informed consent.
- Clear, unobstructed home or indoor/outdoor video recordings showing the dog's full body posture and movement (minimum 30–120 seconds per clip).
- Completion of the baseline C-BARQ questionnaire sections relevant to daily temperament and stress/arousal context.

## Privacy, Consent & Data Handling
- **Explicit Consent Gate**: No video file is ingested or analyzed without recorded consent (`consent_given = True`), matching `SYS-01` and `SYS-02`.
- **Anonymization**: Participants and dogs are assigned coded identifiers (`D01`, `D02`, ...); filenames and metadata strip personal names, addresses, and audio/faces where possible.
- **Local-First Storage**: Collected clips and metadata remain in local access-controlled storage rather than public cloud repositories.

## Recruitment & Intake Tracking Summary
- Outreach shared across local dog-owner communities and interview participants (`P1`–`P5`).
- Intake checklist verified for each submission: consent confirmed, video resolution/lighting checked, and C-BARQ baseline paired with anonymized ID.