# Installs exported custom Codex skills into ~/.codex/skills on Windows.
$ErrorActionPreference = 'Stop'

$SourceDir = Join-Path $PSScriptRoot 'skills'
$TargetDir = Join-Path $HOME '.codex/skills'
$GroupDir = Join-Path $PSScriptRoot 'groups'

New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

function Get-SkillNames {
    param([string[]]$Requested)

    if (-not $Requested -or $Requested.Count -eq 0) {
        return (Get-ChildItem -Path $SourceDir -Directory | Sort-Object Name | Select-Object -ExpandProperty Name)
    }

    $Names = New-Object System.Collections.Generic.List[string]
    foreach ($Item in $Requested) {
        if ($Item -eq 'core' -or $Item -eq 'utility') {
            $GroupFile = Join-Path $GroupDir "$Item.txt"
            if (Test-Path $GroupFile) {
                Get-Content $GroupFile | ForEach-Object {
                    if ($_ -and -not $Names.Contains($_)) {
                        $Names.Add($_)
                    }
                }
            }
        } else {
            if (-not $Names.Contains($Item)) {
                $Names.Add($Item)
            }
        }
    }

    return $Names
}

$SkillNames = Get-SkillNames -Requested $args

$SkillNames | ForEach-Object {
    $SkillName = $_
    $SourcePath = Join-Path $SourceDir $SkillName
    $TargetPath = Join-Path $TargetDir $SkillName

    if (-not (Test-Path $SourcePath)) {
        Write-Warning "Skipping unknown skill: $SkillName"
        return
    }

    if (Test-Path $TargetPath) {
        Remove-Item -Path $TargetPath -Recurse -Force
    }

    Copy-Item -Path $SourcePath -Destination $TargetPath -Recurse -Force
    Write-Host "Installed: $SkillName"
}

Write-Host "Selected custom skills installed to $TargetDir"
