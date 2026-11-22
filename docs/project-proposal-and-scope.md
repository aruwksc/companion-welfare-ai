# Project Proposal & Scope (CWA-4)

## Project Overview
**Companion Welfare AI** is a desktop application designed to support structured, non-diagnostic review of canine behavior from local video recordings, paired with consent tracking, local SQLite persistence, manual timeline annotations, and readable Markdown report exports.

## Objectives
- Provide an intuitive desktop workflow (`PySide6`) for managing dog profiles, explicit owner consent, local video import, and offline behavioral event review.
- Store sessions, detected/manual events, and profile records locally in SQLite without requiring external cloud services.
- Keep outputs transparent and safe by enforcing a clear non-diagnostic notice (`NON_DIAGNOSTIC_NOTICE`) in previews and exported reports.

## Scope Definition
### In Scope (Desktop & Workflow Foundation)
- Dog profile management and explicit owner consent gating (`SYS-01`, `SYS-02`).
- Local video selection, offline analysis execution, and persistent storage in SQLite (`SYS-03`, `SYS-04`).
- Timeline frame inspection, manual event annotations (`is_manual`), and Markdown report export with non-diagnostic disclaimer (`SYS-05`, `SYS-06`).
- Automated test coverage via `pytest` and documentation of requirements, use cases, comparisons, and walkthroughs.

### Out of Scope
- Veterinary medical diagnosis, clinical treatment recommendations, or health/disease claims.
- Mandatory cloud video streaming or proprietary wearable hardware dependencies.
- Unconsented media processing or hidden background data collection.