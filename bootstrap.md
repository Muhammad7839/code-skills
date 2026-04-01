# Bootstrap

Clone and install this repository of custom Codex skills on a local or cloud Codex machine.

```bash
git clone https://github.com/Muhammad7839/code-skills.git
cd code-skills
```

Install all skills:

Windows:
```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

macOS:

```bash
bash install.sh
```

Install only core system skills:

Windows:
```powershell
powershell -ExecutionPolicy Bypass -File install.ps1 core
```

macOS:
```bash
bash install.sh core
```

Manual copy remains available from `skills/<skill-name>/`.
For scripted cloud bootstrap, read `manifest.json`.
