$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Test-Path ".\.venv\Scripts\pyinstaller.exe")) {
    throw "PyInstaller was not found. Run scripts\install.ps1 first."
}

& ".\.venv\Scripts\pyinstaller.exe" voiceflow_ai.spec
