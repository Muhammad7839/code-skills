# Installs exported custom Codex skills into ~/.codex/skills on Windows.
$ErrorActionPreference = 'Stop'

$Installer = Join-Path $PSScriptRoot 'install.py'
python $Installer @args
