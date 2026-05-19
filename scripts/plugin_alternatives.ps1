# Full replacement for Sonatype / Browse MCP / Aikido — no Cursor plugin auth required.
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "=== 1. Fix Browse plugin binary (optional MCP) ===" -ForegroundColor Cyan
& "$PSScriptRoot\fix_cursor_plugins.ps1"

Write-Host "`n=== 2. Security audit (replaces Sonatype + Aikido) ===" -ForegroundColor Cyan
if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    python -m venv .venv
    .\.venv\Scripts\pip install -e ".[dev]" -q
}
.\.venv\Scripts\python scripts\security_audit.py
$auditCode = $LASTEXITCODE

Write-Host "`n=== 3. Pinned versions (replaces Sonatype recommendations) ===" -ForegroundColor Cyan
.\.venv\Scripts\python scripts\pin_versions.py

Write-Host "`n=== 4. Backend tests ===" -ForegroundColor Cyan
.\.venv\Scripts\pytest backend\tests -q
$testCode = $LASTEXITCODE

Write-Host "`n=== 5. Playwright E2E (replaces Browse MCP) ===" -ForegroundColor Cyan
Write-Host "Start backend + frontend in other terminals, or rely on playwright webServer config."
Push-Location e2e
if (-not (Test-Path node_modules)) { npm install }
npx playwright test --reporter=line 2>&1
$e2eCode = $LASTEXITCODE
Pop-Location

Write-Host "`nDone. MCP plugins are optional; this script covers their jobs." -ForegroundColor Green
exit [Math]::Max($auditCode, [Math]::Max($testCode, $e2eCode))
