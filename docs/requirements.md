# System Requirements Referenced by the Architecture

These system-level requirements provide a traceable baseline for the architecture diagram. They are project requirements, not claims that the corresponding features are already implemented. Technology choices remain open until their ADRs are accepted.

| ID | Requirement | Architecture element | Verification evidence |
|---|---|---|---|
| SYS-01 | Imported video and sampled frames remain on the user's device during analysis. | Local video folder; local ML worker | Verify the processing path and monitor network activity during a consented test session. |
| SYS-02 | The desktop UI sends application commands through the Application API; it does not access persisted data directly. | Desktop UI; Application API; repository | Review component dependencies and run an integration scenario through the UI/API. |
| SYS-03 | Analysis runs through a worker boundary and returns observable events with intervals, confidence, and model version. | Analysis orchestrator; ML worker; model package | Run an end-to-end analysis and inspect its documented event schema and model metadata. |
| SYS-04 | Profiles, consent state, session metadata, and analysis events are persisted through the repository using a local storage driver. | Repository; local database | Inspect repository access and verify local write/read behaviour. The production storage technology is pending ADR-0004. |
| SYS-05 | Behaviour output describes visible observations and uncertainty; it must not be presented as a veterinary diagnosis. | Classifier; timeline; report service | Review ambiguous-case handling and verify the non-diagnostic notice appears in results and reports. |
| SYS-06 | The user can review the timeline and preview or export a report containing event time, label, confidence, model version, and a non-diagnostic notice. | Desktop UI; timeline; report service | Complete a report-preview/export scenario and inspect the resulting fields. |

## Open architecture decisions

- **D1 / ADR-0001:** desktop platform and UI framework — canonical decision record not present in this checkout.
- **D4 / ADR-0004:** local database/storage driver — canonical decision record not present in this checkout.
