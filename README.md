# Custom Codex Skills

This repository stores user-created Codex skills exported from `~/.codex/skills/`.
Only physical custom skill folders that include `SKILL.md` are included.

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

## Install

### Windows
```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

### macOS/Linux
```bash
bash install.sh
```

## Use
After install, the skills are available under `~/.codex/skills/<skill-name>/`.
You can reference each skill by folder name when invoking Codex workflows.
