# Windows-friendly task runner (replaces GNU Make when "make" is not installed).
# Usage from repo root:  .\tasks.ps1 install | migrate | backend | frontend | test | help
# From frontend/:       .\tasks.ps1 frontend  (forwards to this file)
param(
    [Parameter(Position = 0)]
    [string]$Target = "help"
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$Py = Join-Path $Root ".venv\Scripts\python.exe"
$Pip = Join-Path $Root ".venv\Scripts\pip.exe"
$Uvicorn = Join-Path $Root ".venv\Scripts\uvicorn.exe"

function Import-DotEnv {
    $envFile = Join-Path $Root ".env"
    if (-not (Test-Path $envFile)) { return }
    Get-Content $envFile | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#")) { return }
        $eq = $line.IndexOf("=")
        if ($eq -lt 1) { return }
        $key = $line.Substring(0, $eq).Trim()
        $val = $line.Substring($eq + 1).Trim()
        if ($val.StartsWith('"') -and $val.EndsWith('"')) { $val = $val.Substring(1, $val.Length - 2) }
        if ([string]::IsNullOrWhiteSpace($key)) { return }
        if (-not [Environment]::GetEnvironmentVariable($key, "Process")) {
            Set-Item -Path "env:$key" -Value $val
        }
    }
}

Import-DotEnv

function Get-ApiPort {
    if ($env:API_PORT) { return [int]$env:API_PORT }
    return 8000
}

function Get-UiPort {
    if ($env:VITE_PORT) { return [int]$env:VITE_PORT }
    return 5173
}

function Get-ListenersOnPort([int]$Port) {
    $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if (-not $conns) { return @() }
    return @($conns | Select-Object -ExpandProperty OwningProcess -Unique | Where-Object { $_ })
}

function Get-OrphanSpawnPids([int]$ParentPid) {
    $pattern = "parent_pid=$ParentPid\b"
    return @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -and $_.CommandLine -match $pattern } |
        Select-Object -ExpandProperty ProcessId)
}

function Stop-ProcessTree([int]$ProcId) {
    if (-not $ProcId) { return }
    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.ParentProcessId -eq $ProcId } |
        ForEach-Object { Stop-ProcessTree $_.ProcessId }
    Stop-Process -Id $ProcId -Force -ErrorAction SilentlyContinue
    $prevEap = $ErrorActionPreference
    $ErrorActionPreference = "SilentlyContinue"
    try {
        & taskkill.exe /F /PID $ProcId /T 2>&1 | Out-Null
    } finally {
        $ErrorActionPreference = $prevEap
    }
}

function Stop-ViteProjectWorkers {
    $frontendEsc = [regex]::Escape((Join-Path $Root "frontend"))
    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object {
            $cmd = $_.CommandLine
            if (-not $cmd) { return $false }
            ($cmd -match "vite") -and ($cmd -match $frontendEsc)
        } |
        ForEach-Object {
            Write-Host "Stopping Vite worker PID $($_.ProcessId)..."
            Stop-ProcessTree $_.ProcessId
        }
}

function Stop-UvicornProjectWorkers {
    $rootEsc = [regex]::Escape($Root)
    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object {
            $cmd = $_.CommandLine
            if (-not $cmd) { return $false }
            ($cmd -match "uvicorn") -and ($cmd -match $rootEsc -or $cmd -match "backend\.main:app")
        } |
        ForEach-Object {
            Write-Host "Stopping uvicorn worker PID $($_.ProcessId)..."
            Stop-ProcessTree $_.ProcessId
        }
}

function Stop-ProcessOnPort([int]$Port) {
    $attempts = 3
    for ($i = 1; $i -le $attempts; $i++) {
        $pids = Get-ListenersOnPort $Port
        if ($pids.Count -eq 0) { return $true }
        foreach ($procId in $pids) {
            $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
            $name = if ($proc) { $proc.ProcessName } else { "gone" }
            Write-Host "Stopping PID $procId ($name) on port $Port (attempt $i/$attempts)..."
            if ($proc) {
                Stop-ProcessTree $procId
            } else {
                $orphans = Get-OrphanSpawnPids $procId
                if ($orphans.Count -gt 0) {
                    Write-Host "Parent $procId is gone; stopping $($orphans.Count) orphan worker(s)..."
                    foreach ($childId in $orphans) { Stop-ProcessTree $childId }
                }
            }
        }
        if ($Port -eq (Get-ApiPort)) { Stop-UvicornProjectWorkers }
        if ($Port -eq (Get-UiPort)) { Stop-ViteProjectWorkers }
        Start-Sleep -Seconds 2
    }
    return ((Get-ListenersOnPort $Port).Count -eq 0)
}

function Assert-Venv {
    if (-not (Test-Path $Py)) {
        Write-Error "Virtualenv not found. Run:  .\tasks.ps1 install"
        exit 1
    }
}

function Start-Frontend {
    Set-Location $Root
    $uiPort = Get-UiPort
    if (-not (Stop-ProcessOnPort $uiPort)) {
        Write-Error "Port $uiPort is still in use. Run:  .\tasks.ps1 frontend-stop   Or:  `$env:VITE_PORT = 5174"
        exit 1
    }
    $frontendDir = Join-Path $Root "frontend"
    if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
        Write-Host "node_modules missing - running npm install..."
        Push-Location $frontendDir
        npm install
        Pop-Location
    }
    Write-Host "Starting UI at http://127.0.0.1:$uiPort"
    Push-Location $frontendDir
    if ($env:VITE_PORT) {
        npm run dev -- --port $uiPort
    } else {
        npm run dev
    }
}

function Start-Backend {
    Assert-Venv
    Set-Location $Root
    $port = Get-ApiPort
    if (-not (Stop-ProcessOnPort $port)) {
        Write-Error "Port $port is still in use. Run:  .\tasks.ps1 backend-stop   Or:  `$env:API_PORT = 8010"
        exit 1
    }
    Write-Host "Starting API at http://127.0.0.1:$port/docs"
    & $Uvicorn backend.main:app --reload --host 127.0.0.1 --port $port
}

function Show-Help {
    $apiPort = Get-ApiPort
    $uiPort = Get-UiPort
    Write-Host ""
    Write-Host "Supply Chain Command Center - tasks.ps1"
    Write-Host ""
    Write-Host "  install          venv + pip + npm install"
    Write-Host "  migrate          Initialize DuckDB schema"
    Write-Host "  backend          API on port $apiPort (auto-frees port)"
    Write-Host "  backend-stop     Stop listener on API port"
    Write-Host "  frontend         Vite UI on port $uiPort (auto-frees port)"
    Write-Host "  frontend-stop    Stop listener on UI port"
    Write-Host "  test             pytest"
    Write-Host "  test-e2e         Playwright E2E"
    Write-Host "  health           Data-source health CLI"
    Write-Host "  audit            pip-audit + npm audit"
    Write-Host "  pins             Dependency versions"
    Write-Host "  plugin-check     Audit + tests + E2E"
    Write-Host "  fix-browse       Repair Browse MCP binary (optional)"
    Write-Host ""
    Write-Host "Run from repo root: $Root"
    Write-Host "From frontend/: use .\tasks.ps1 (forwards here)"
    Write-Host ""
    Write-Host "Ports: set API_PORT or VITE_PORT in .env or environment"
    Write-Host ""
}

switch ($Target.ToLower()) {
    "help" { Show-Help; exit 0 }
    "install" {
        Set-Location $Root
        if (-not (Test-Path ".venv")) { python -m venv .venv }
        & $Pip install -e ".[dev]"
        Push-Location (Join-Path $Root "frontend")
        npm install
        Pop-Location
        Write-Host "Done. Next: .\tasks.ps1 migrate"
    }
    "migrate" {
        Assert-Venv
        Set-Location $Root
        & $Py -m backend.db.migrate
    }
    "backend" { Start-Backend }
    "backend-stop" {
        $port = Get-ApiPort
        if (Stop-ProcessOnPort $port) {
            Write-Host "Port $port is free."
        } else {
            Write-Warning "Port $port may still be in use."
        }
    }
    "frontend" { Start-Frontend }
    "frontend-stop" {
        $uiPort = Get-UiPort
        if (Stop-ProcessOnPort $uiPort) {
            Write-Host "Port $uiPort is free."
        } else {
            Write-Warning "Port $uiPort may still be in use."
        }
    }
    "test" {
        Assert-Venv
        Set-Location $Root
        & $Py -m pytest backend/tests -q
    }
    "health" {
        Assert-Venv
        Set-Location $Root
        & $Py -m backend.scripts.health_check
    }
    "audit" {
        Assert-Venv
        Set-Location $Root
        & $Py (Join-Path $Root "scripts\security_audit.py")
    }
    "audit-all" {
        Assert-Venv
        Set-Location $Root
        & $Py (Join-Path $Root "scripts\security_audit.py")
    }
    "pins" {
        Assert-Venv
        Set-Location $Root
        & $Py (Join-Path $Root "scripts\pin_versions.py")
    }
    "fix-browse" {
        & powershell -ExecutionPolicy Bypass -File (Join-Path $Root "scripts\fix_cursor_plugins.ps1")
    }
    "plugin-check" {
        & powershell -ExecutionPolicy Bypass -File (Join-Path $Root "scripts\plugin_alternatives.ps1")
    }
    "test-e2e" {
        Push-Location (Join-Path $Root "e2e")
        npm install
        npx playwright install chromium
        npx playwright test
        Pop-Location
    }
    default {
        Write-Error "Unknown target '$Target'. Run:  .\tasks.ps1 help"
        exit 1
    }
}
