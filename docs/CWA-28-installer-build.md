# CWA-28 Installer Build and Verification

## Prototype scope

The CWA-28 spike provides a small Windows desktop window and a local SQLite read/write check. The implementation uses Python 3.11+, Tkinter, and the standard-library `sqlite3` adapter. The D1 and D4 choices are provisional pending review of the canonical ADR-0001 and ADR-0004. See `docs/adr/CWA-28-provisional-decisions.md`.

The installer is designed to install the application under Program Files. Runtime data is created per user under `%LOCALAPPDATA%\CompanionWelfareAI`, not in the installation directory. The prototype writes only a demonstration greeting; it does not process dog videos or store animal profiles.

## Build on Windows

Prerequisites:

- Python 3.11 or newer with the Python Launcher (`py.exe`)
- Internet access during the first build to install PyInstaller
- Inno Setup 6 to compile the Windows setup executable

From the repository root, run:

```powershell
.\scripts\build-windows-installer.ps1
```

The script creates a local `.venv-build`, installs the project and PyInstaller, creates a one-folder app in `dist/CompanionWelfareAI`, and compiles `dist/installer/CompanionWelfareAI-Setup-0.1.0.exe` with Inno Setup. Build outputs and the virtual environment are ignored by Git.

## Local smoke check

Launch `dist/CompanionWelfareAI/CompanionWelfareAI.exe` or install the setup executable. Select **Run local storage check**. The app should show `PASS`, a per-user database path, and an increasing record count after each click. Close and reopen the app and repeat the check to confirm that the database persists.

## Clean-VM acceptance test

Install and run the generated setup executable on a clean Windows VM that does not have Python installed. Record the installer file size and elapsed installation time. Verify Start Menu launch, the local storage check, persistence after restart, and uninstall. Record observations and add a privacy-safe screenshot to `docs/evidence/`. Use `docs/evidence/CWA-28-clean-vm-test-template.md`; do not replace `NOT RUN` with `PASS` until the VM test is actually complete.

## ADR review gate

The repository currently contains no ADR-0001 or ADR-0004 files. Do not claim that the decisions are confirmed. Before accepting this spike, link the existing canonical ADRs, review the provisional Tkinter and SQLite choices with the team, and record whether each ADR is accepted or reopened with rationale.
