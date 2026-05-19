# Repairs Browse MCP binary (npm install in plugin cache). Safe to re-run.
$BrowseRoot = "$env:USERPROFILE\.cursor\plugins\cache\cursor-public\browse"
$VersionDir = Get-ChildItem -Path $BrowseRoot -Directory | Sort-Object Name -Descending | Select-Object -First 1
if (-not $VersionDir) {
    Write-Host "Browse plugin cache not found under $BrowseRoot"
    exit 1
}
$PluginPath = $VersionDir.FullName
Write-Host "Running npm install in $PluginPath ..."
Push-Location $PluginPath
npm install --no-fund --no-audit 2>&1
$bin = Join-Path $PluginPath "node_modules\.bin\browse.cmd"
Pop-Location
if (Test-Path $bin) {
    Write-Host "OK: browse.cmd exists. Browse MCP may still fail on Windows (Cursor spawns 'browse' without .cmd)."
    Write-Host "Use: make test-e2e  (Playwright) instead."
    exit 0
}
Write-Host "WARN: browse.cmd still missing after npm install."
exit 1
