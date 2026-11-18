# CWA-27: Verification and Usability Study Protocol

## 1. Purpose

This protocol defines how the Companion Welfare AI prototype will be verified and how a small formative usability study will be conducted. It is a plan; results must be added only after the tests have actually been run. The prototype is an observation aid and must not be presented as a veterinary diagnostic system.

## 2. Test strategy

Run tests in the following order. Record the application version/commit, operating system, hardware, test data identifier, date, expected result, observed result, status, and evidence for each test.

| Level | What is checked | Example checks | Evidence |
|---|---|---|---|
| Unit | Individual functions and validation rules | Video metadata validation; timestamp interval handling; low-confidence keypoint filtering; feature calculations; event-schema validation; report formatting | Test output and coverage summary |
| Integration | Interfaces between modules | Video importer to local storage; analysis orchestrator to pose/classification adapters; analysis result to repository; repository to timeline/report | Integration test output and relevant logs |
| System | Full application on the target desktop | Create a dog profile; import a permitted test video; analyse; inspect/edit an event; export a report; delete the session | Completed test checklist, screenshots without personal data, logs |
| Acceptance | Requirements and user scenarios | Confirm every Must requirement has a test; verify privacy notice/disclaimer; verify normal and error scenarios | Requirements-to-test traceability table and sign-off |

### Test data and conditions

- Use synthetic or consented test videos. Keep raw videos and consent forms outside Git in the approved private location.
- Include at least one valid video, one unsupported file, one unreadable/corrupted video, one low-light or partially occluded clip, and one clip with no dog visible.
- Use the same documented video, model, frame-sampling settings, and reference laptop when comparing repeated performance measurements.
- Test normal use, invalid input, cancellation, deletion, and recovery after an analysis error.
- Do not use public videos or images unless their exact usage rights have been checked and documented.

## 3. Proposed quality gates

These are proposed project gates for team agreement. They are not claims that the current prototype already passes.

1. **Requirements gate:** 100% of Must requirements have a linked verification case and a recorded result before the pre-defence release.
2. **Automated-test gate:** all required unit and integration tests pass on the submitted commit; failures are either fixed or explicitly documented with an owner and reason.
3. **Critical-defect gate:** no open critical/high-severity defect that blocks video import, analysis, result review, local deletion, or report export.
4. **Privacy gate:** test videos and profiles remain local; no raw media or personal data is committed to Git; deletion is verified in the configured storage location.
5. **Performance gate:** report processing time and FPS on the reference desktop with hardware and settings recorded. Use CWA-20's agreed threshold once the team has approved it; do not substitute Colab GPU results for desktop measurements.
6. **Usability gate:** each critical task is completed successfully by at least 4 of 5 formative-study participants without moderator intervention; no unresolved critical usability issue remains. If fewer than five participants are available, report the actual count and treat the result as exploratory.
7. **SUS gate:** report all valid participant scores and the sample mean and median. A mean SUS score of 68 or above is a provisional target for the formative study, not proof of usability or a statistically generalisable result. Investigate any lower score and report the limitations of the small sample.

## 4. Defect severity and release decision

| Severity | Definition | Release handling |
|---|---|---|
| Critical | Data loss, privacy breach, application cannot start, or core workflow cannot be completed | Must be fixed and retested before release |
| High | Major workflow fails or results are misleading with no clear recovery | Must be fixed or release blocked; any exception requires documented team/supervisor decision |
| Medium | A feature is impaired but a clear workaround exists | Record workaround and owner; decide with the team whether it blocks the milestone |
| Low | Cosmetic or minor wording/layout issue | Log and prioritise for a later iteration |

The release decision must list the tested commit, passed/failed gates, open defects, known limitations, and approver. A test that was not run must be marked `NOT RUN`, not `PASS`.

## 5. Usability study plan

### Participants

Recruit five participants for a formative prototype study if available: ideally dog owners or people who would plausibly review companion-dog behaviour records. Participation is voluntary. Obtain the required consent before collecting responses. Do not collect names in the analysis sheet; use participant IDs such as `U01` to `U05`. Do not record video of participants unless separate consent explicitly permits it.

### Setup and moderator instructions

- Use the same application build, test profile, and consented/synthetic video set for all participants.
- Conduct sessions individually, approximately 20–30 minutes each.
- Explain that the prototype estimates visible behaviour and is not a diagnosis. Tell participants that the video is test material and explain how session data will be handled.
- Ask participants to think aloud while completing tasks. The moderator must not guide them unless they are stuck; record when help is given.
- Do not coach a participant toward the expected answer. After each task, ask what they expected and what was confusing.
- Stop the session if the participant wishes to withdraw or if the test data raises a privacy concern.

### User tasks

| ID | Task prompt to participant | Success criterion | Record |
|---|---|---|---|
| U1 | Create a profile for the provided test dog and review the consent/privacy information. | Profile is saved with the test values; participant can identify where the consent/privacy choice is shown. | Completion, time, errors, help needed |
| U2 | Import the provided valid test video and start an analysis. | Correct video is selected; analysis begins; progress is visible. | Completion, time, errors, help needed |
| U3 | Find one detected event on the timeline and explain what the displayed label and confidence mean. | Participant locates an event and correctly understands that it is an observable estimate, not a diagnosis. | Completion, interpretation issue, help needed |
| U4 | Mark an event as uncertain or correct its label, then save the change. | The edit is saved and visible after reopening the session. | Completion, time, errors, help needed |
| U5 | Preview and export a report, then locate the non-diagnostic disclaimer. | Report is previewed/exported and disclaimer is found. | Completion, time, errors, help needed |
| U6 | Delete the test session/video using the application controls. | The application confirms deletion and the test item is absent from the configured local storage. | Completion and deletion evidence |

### Usability success measures

- **Task completion:** percentage of participants who complete each task without moderator help. Also report completion with help separately.
- **Time on task:** time from reading the prompt to successful completion; report median and range because the sample is small.
- **Errors:** count mis-selections, failed actions, lost changes, and incorrect interpretations of labels/confidence.
- **Critical usability issues:** problems that prevent completion, risk accidental disclosure/deletion, or cause a participant to treat an output as a diagnosis.
- **Qualitative feedback:** record anonymised observations and short paraphrases; do not attribute comments to identifiable participants.

## 6. System Usability Scale (SUS) procedure

Use the standard 10-item SUS questionnaire after the participant has completed the tasks and before the debrief. Keep the standard item wording, order, and five-point response scale unchanged. Do not rewrite the questionnaire as project-specific statements; explain terms before the session instead.

Score each response from 1 to 5. For odd-numbered items, subtract 1 from the response. For even-numbered items, subtract the response from 5. Add the ten adjusted values and multiply the sum by 2.5. The resulting participant score ranges from 0 to 100. Report the number of valid responses, each anonymised score, mean, median, and range. Do not interpret an individual score as a percentage or treat the SUS result as a substitute for task-completion evidence.

Use the original SUS source for the questionnaire and scoring procedure: John Brooke, “SUS: A quick and dirty usability scale,” in *Usability Evaluation in Industry* (1996). The SUS is a perceived-usability measure; the study's task observations provide separate effectiveness and efficiency evidence.

## 7. Results template

Complete this table only after running the study:

| Measure | Result | Evidence / notes |
|---|---|---|
| Application commit/version | NOT RUN | |
| Test environment | NOT RUN | |
| Participants recruited/completed | NOT RUN | |
| U1–U6 task completion | NOT RUN | |
| Median time per task | NOT RUN | |
| Errors and critical usability issues | NOT RUN | |
| SUS individual scores, mean and median | NOT RUN | |
| Passed/failed/not-run quality gates | NOT RUN | |
| Known limitations and follow-up actions | NOT RUN | |

## 8. Acceptance criteria for CWA-27

CWA-27 is ready for review when the repository contains the agreed test levels and quality gates, the usability task script and success criteria, the SUS procedure and scoring formula, and the results template. The team has reviewed and agreed the proposed thresholds. Actual outcomes remain `NOT RUN` until supported by test evidence.

## References

- Brooke, J. (1996). “SUS: A quick and dirty usability scale.” In *Usability Evaluation in Industry*. [Original chapter scan](https://hci-studies.org/methods-and-measures/downloads/SUS_Brooke1996.pdf).
- Digital.gov. “How to conduct a usability test.” [Guide](https://digital-gov-static-prod.app.cloud.gov/resources/how-conduct-usability-test).