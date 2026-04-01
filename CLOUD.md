# Cloud Codex Setup

Use this repo as the single source for your custom Codex skills on any cloud machine.

## Fastest path

```bash
git clone https://github.com/Muhammad7839/code-skills.git
cd code-skills
python3 install.py core
```

Install all skills:

```bash
python3 install.py
```

Install only selected skills:

```bash
python3 install.py fitgpt-dev-orchestrator git-preflight bug-hunter
```

## What Codex should do

If you want to instruct Codex directly on a cloud machine, this is the simplest wording:

```text
Clone https://github.com/Muhammad7839/code-skills, run python3 install.py core, and load the skills from ~/.codex/skills.
```

For all skills:

```text
Clone https://github.com/Muhammad7839/code-skills, run python3 install.py, and load the skills from ~/.codex/skills.
```

## Why this is safe

- `install.py` reads `manifest.json`
- only listed custom skills are copied
- existing skill folders are backed up before replacement
- built-in `.system` skills are not part of the repo
- the canonical install location stays `~/.codex/skills`
