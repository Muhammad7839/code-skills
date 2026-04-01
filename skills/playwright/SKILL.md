---
name: "playwright"
description: "Use when the task requires automating a real browser from the terminal (navigation, form filling, snapshots, screenshots, data extraction, UI-flow debugging) via `playwright-cli` or the bundled wrapper script."
---

# Playwright CLI Skill

## Skill Group
Utility skill

## Purpose
Automate a real browser from the terminal with `playwright-cli`, preferably through the bundled wrapper script.

## Modes
### Read / Analyze
- Confirm the environment can run the wrapper.
- Open pages, capture snapshots, inspect refs, and diagnose UI state.
- Re-snapshot after navigation or DOM changes before issuing ref-based commands.

### Execution
- Drive the browser with explicit CLI commands.
- Capture screenshots, PDFs, or traces when useful.
- Produce a reusable command sequence or script when the task needs repeatability.

## Run Logging
Record one Markdown log per run:
```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export SKILL_LOGGER="$CODEX_HOME/skills/fitgpt-dev-orchestrator/scripts/skill_run_log.py"
RUN_LOG=$(python3 "$SKILL_LOGGER" --skill "playwright" --action "automate <browser-flow>" --status started)
# ...run the browser flow...
python3 "$SKILL_LOGGER" --skill "playwright" --action "automate <browser-flow>" --status success --log-file "$RUN_LOG"
# on failure: use --status failure
```

## Setup
1. Confirm `npx` is available.
2. Set:
```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export PWCLI="$CODEX_HOME/skills/playwright/scripts/playwright_cli.sh"
```
3. Prefer `"$PWCLI"` over a global install.

## Core Loop
1. Open the page
2. Snapshot
3. Interact using current refs
4. Snapshot again after meaningful UI changes
5. Capture artifacts if needed

## Guardrails
- Always snapshot before using element refs.
- Re-snapshot when refs may be stale.
- Prefer explicit CLI commands over `eval` or `run-code`.
- Use `--headed` when visual verification helps.
- Store repo artifacts under `output/playwright/`.
