# Bootstrap

Clone and install this repository of custom Codex skills on a local or cloud Codex machine.

```bash
git clone https://github.com/Muhammad7839/code-skills.git
cd code-skills
```

Preferred install path on any cloud or Linux machine:

```bash
python3 install.py core
```

Install all skills:

```bash
python3 install.py
```

Install all skills with OS-specific wrappers:

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
For scripted cloud bootstrap, use `install.py` or read `manifest.json`.
