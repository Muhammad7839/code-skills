# Custom Codex Skills

This repository stores user-created Codex skills exported from `~/.codex/skills/`.
It is organized for two use cases:
- cloud or scripted install from a clean machine
- manual copy of individual skill folders at any time

Only custom skills are included. Built-in `.system` skills, logs, and temp files are excluded.

## Repository Layout
- `skills/<skill-name>/`: canonical skill folders to copy or install
- `manifest.json`: machine-readable catalog for cloud or scripted extraction
- `groups/core.txt`: core system skill list
- `groups/utility.txt`: utility skill list
- `install.sh` and `install.ps1`: selective installers for macOS/Linux and Windows

## Exported Skills
- bug-hunter
- codebase-auditor
- doc
- fitgpt-dev-orchestrator
- fitgpt-stack-engineer
- git-preflight
- pdf
- playwright
- senior-fullstack-engineer
- sora
- spreadsheet

## Skill Groups
### Core
- fitgpt-dev-orchestrator
- git-preflight
- codebase-auditor
- bug-hunter
- fitgpt-stack-engineer
- senior-fullstack-engineer

### Utility
- pdf
- spreadsheet
- sora
- playwright
- doc

## Install

### Windows
```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

### macOS/Linux
```bash
bash install.sh
```

Install a specific group:

```bash
bash install.sh core
bash install.sh utility
```

Install only selected skills:

```bash
bash install.sh fitgpt-dev-orchestrator git-preflight
```

Windows examples:

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1 core
powershell -ExecutionPolicy Bypass -File install.ps1 fitgpt-dev-orchestrator git-preflight
```

## Manual Copy
Copy any folder from `skills/<skill-name>/` into `~/.codex/skills/<skill-name>/`.

Examples:

```bash
cp -R skills/fitgpt-dev-orchestrator ~/.codex/skills/
cp -R skills/bug-hunter ~/.codex/skills/
```

On a cloud machine, clone the repo and either:
- run the installer
- copy the needed folders manually
- read `manifest.json` to automate extraction
