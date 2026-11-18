$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonLauncher = Get-Command py -ErrorAction SilentlyContinue
if (-not $pythonLauncher) {
    throw "Python Launcher (py.exe) was not found. Install Python 3.11 or newer and enable the launcher."
}

$venvPath = Join-Path $repoRoot ".venv-build"
$venvPython = Join-Path $venvPath "Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    & py -3 -m venv $venvPath
}

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -e "${repoRoot}[build]"
if ($LASTEXITCODE -ne 0) { throw "Python build dependencies could not be installed." }

Push-Location $repoRoot
try {
    & $venvPython -m PyInstaller --noconfirm --clean --windowed --onedir `
        --name CompanionWelfareAI --paths src `
        src\companion_welfare_ai\app\main.py
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed." }

    $isccCandidates = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
    )
    $iscc = $isccCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $iscc) {
        throw "Inno Setup 6 (ISCC.exe) was not found. The packaged app is in dist\CompanionWelfareAI; install Inno Setup 6 to build the installer."
    }

    New-Item -ItemType Directory -Force -Path dist\installer | Out-Null
    & $iscc packaging\windows\companion-welfare-ai.iss
    if ($LASTEXITCODE -ne 0) { throw "Inno Setup compilation failed." }
    Write-Host "Installer created: dist\installer\CompanionWelfareAI-Setup-0.1.0.exe"
}
finally {
    Pop-Location
}
