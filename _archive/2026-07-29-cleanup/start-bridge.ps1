$ErrorActionPreference = "Stop"
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $dir ".venv\Scripts\python.exe"
$script = Join-Path $dir "app.py"
$log = Join-Path $dir "logs\bridge.log"

Set-Location $dir
& $python $script *>> $log
