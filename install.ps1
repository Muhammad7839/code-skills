# Installs all exported custom Codex skills into ~/.codex/skills on Windows.
$ErrorActionPreference = 'Stop'

$SourceDir = Join-Path $PSScriptRoot 'skills'
$TargetDir = Join-Path $HOME '.codex/skills'

New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

Get-ChildItem -Path $SourceDir -Directory | ForEach-Object {
    $SkillName = $_.Name
    $TargetPath = Join-Path $TargetDir $SkillName

    if (Test-Path $TargetPath) {
        Remove-Item -Path $TargetPath -Recurse -Force
    }

    Copy-Item -Path $_.FullName -Destination $TargetPath -Recurse -Force
    Write-Host "Installed: $SkillName"
}

Write-Host "All custom skills installed to $TargetDir"
