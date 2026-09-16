$ErrorActionPreference = "Stop"
$SourceDir = Split-Path -Parent $PSScriptRoot
$TargetRoot = Join-Path $env:APPDATA "Autodesk\Autodesk Fusion 360\API\AddIns"
$TargetDir = Join-Path $TargetRoot "MakeOrbitGearGenerator"
$BackupDir = "$TargetDir.previous"

New-Item -ItemType Directory -Force -Path $TargetRoot | Out-Null
if (Test-Path $BackupDir) { Remove-Item -Recurse -Force $BackupDir }
if (Test-Path $TargetDir) { Move-Item $TargetDir $BackupDir }
Copy-Item -Recurse -Force $SourceDir $TargetDir
Get-ChildItem -Path $TargetDir -Directory -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force

Write-Host "MakeOrbit GearGenerator installed at:"
Write-Host $TargetDir
Write-Host "Restart Autodesk Fusion or start the add-in from Scripts and Add-ins."
Read-Host "Press Enter to close"
