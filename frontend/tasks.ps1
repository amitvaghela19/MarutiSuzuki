# Run from frontend/ — forwards to repo-root tasks.ps1
param([Parameter(Position = 0)][string]$Target = "help")
$RootTasks = Join-Path (Split-Path $PSScriptRoot -Parent) "tasks.ps1"
if (-not (Test-Path $RootTasks)) {
    Write-Error "Root tasks.ps1 not found at $RootTasks. Run from e:\Amit\MarutiSuzuki instead."
    exit 1
}
& $RootTasks $Target
