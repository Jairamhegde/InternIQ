# InternIQ Development Launcher (PowerShell)
param(
    [string]$HostName = "127.0.0.1",
    [int]$Port = 8000,
    [switch]$NoReload,
    [switch]$Separate,
    [switch]$KillExisting
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Check virtual environment python
$pythonCmd = "python"
if (Test-Path "$scriptDir\scraperenv\Scripts\python.exe") {
    $pythonCmd = "$scriptDir\scraperenv\Scripts\python.exe"
} elseif (Test-Path "$scriptDir\.venv\Scripts\python.exe") {
    $pythonCmd = "$scriptDir\.venv\Scripts\python.exe"
} elseif (Test-Path "$scriptDir\venv\Scripts\python.exe") {
    $pythonCmd = "$scriptDir\venv\Scripts\python.exe"
}

$argsList = @("$scriptDir\run_dev.py", "--host", $HostName, "--port", $Port)
if ($NoReload) { $argsList += "--no-reload" }
if ($Separate) { $argsList += "--separate" }
if ($KillExisting) { $argsList += "--kill-existing" }

& $pythonCmd $argsList
