# CWA-28 Provisional Technology Decisions

## Repository review

The project checkout used for this spike does not contain decision records named ADR-0001 or ADR-0004. Therefore, this work cannot honestly mark those ADRs as accepted or confirmed. The team should link the canonical ADRs and decide whether to accept or reopen them before treating this spike as the production platform decision.

## D1 — Desktop platform (proposal for CWA-28 only)

- **Status:** Provisional; team confirmation required.
- **Spike choice:** Python 3.11+ with the standard-library Tkinter GUI.
- **Reason:** It demonstrates a local desktop window without adding a GUI package dependency, keeping this hello-world packaging spike small.
- **Limitations:** Tkinter is only a packaging/storage proof. It does not establish the final UI toolkit, accessibility, or production UX suitability.
- **Decision needed:** Compare this proposal with the platform recorded in ADR-0001. Accept it for the prototype or reopen ADR-0001 with rationale.

## D4 — Local storage (proposal for CWA-28 only)

- **Status:** Provisional; team confirmation required.
- **Spike choice:** Python `sqlite3` with a per-user local database under `%LOCALAPPDATA%\CompanionWelfareAI` on Windows.
- **Reason:** It validates a serverless local read/write path using the Python standard library and avoids putting runtime data in the installation directory.
- **Limitations:** This is a minimal proof only; encryption, migrations, backup, deletion policy, and concurrent access have not been implemented or validated.
- **Decision needed:** Compare this proposal with the platform/storage driver in ADR-0004. Accept it for the prototype or reopen ADR-0004 with rationale.

## CWA-28 outcome

The prototype may demonstrate the proposed D1 and D4 adapters, but it does not confirm the team-level ADRs. Record the team decision and reviewer in this file or link the canonical ADR records before marking that acceptance criterion complete.
