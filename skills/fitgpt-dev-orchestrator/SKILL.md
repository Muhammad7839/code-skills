---
name: fitgpt-dev-orchestrator
description: Run FitGPT with one repeatable operating procedure every session across macOS and Windows. Use when inspecting repo safety, comparing backend-features against dieuni, main, and all other branches, validating local versus production API routing, starting local services, debugging integration failures, and recommending the next safe move without destructive Git actions.
---

# FitGPT Dev Orchestrator

## Skill Group
Core system skill

## Purpose
Run the standard FitGPT operating procedure for repository safety, branch analysis, environment checks, local startup, and integration triage.

## Modes
### Read / Analyze
- Resolve the FitGPT repo root and confirm `backend/`, `web/`, and `scripts/`.
- Inspect repo safety, branch state, environment routing, and local versus production assumptions.
- Use dependency skills only when they are relevant to the current task.

### Execution
- Run the helper script for report, probe, and startup flows when the task calls for active validation.
- Start local services only after safety and branch checks are complete.
- Apply code or env changes only when the user explicitly asks for fixes.

## Run Logging
Record one Markdown log per run:
```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export SKILL_LOGGER="$CODEX_HOME/skills/fitgpt-dev-orchestrator/scripts/skill_run_log.py"
RUN_LOG=$(python3 "$SKILL_LOGGER" --skill "fitgpt-dev-orchestrator" --action "orchestrate <fitgpt-task>" --status started)
# ...run the orchestration flow...
python3 "$SKILL_LOGGER" --skill "fitgpt-dev-orchestrator" --action "orchestrate <fitgpt-task>" --status success --log-file "$RUN_LOG"
# on failure: use --status failure
```

Logs are stored under `$CODEX_HOME/skill-logs/YYYY-MM-DD/` as one readable Markdown file per run.

## Core Skill Routing
Select only the relevant core system skill for the current request. Do not load all skills automatically.

- Git issue or repo safety concern -> `Git Preflight`
- Debugging, startup failure, auth failure, routing issue, or broken integration -> `Bug Hunter`
- Architecture review, repository mapping, or deployment-risk analysis -> `Codebase Auditor`
- FitGPT backend plus Android integration work -> `FitGPT Stack Engineer`
- Production hardening, release readiness, or minimal production-ready fixes -> `Senior Full-Stack Engineer`

Do not auto-load utility skills from the orchestrator. Utility skills are direct-use tools for document, browser, media, and file-format tasks.

## Core Tooling
Use `scripts/fitgpt_orchestrator.py` for standard reports, branch summaries, env inspection, API probes, and detached local startup.

Before repeating a failed flow, read recent skill logs and reuse the failure context:
- detect repeated failures for the same action
- suggest the next safer core skill or smaller fix path
- avoid rerunning the same failed action unless new evidence justifies it

## Operating Rules
- Treat `dieuni` as read-only comparison input.
- Never commit, push, merge, reset, rebase, force-push, or delete branches unless the user explicitly asks.
- Never overwrite `.env`, `.env.local`, or `.env.production` silently.
- Switch frontend API targets through environment variables, not ad hoc runtime rewrites.
- Do not run `scripts/bootstrap.ps1` or `scripts/bootstrap.sh` automatically.

## Standard Flow
1. Read recent logs for repeated failures and skipped actions
2. Repo safety snapshot when Git context matters
3. Branch analysis against `backend-features`, `dieuni`, and `main` when relevant
4. Environment routing inspection when routing or production context matters
5. Connection checks and local probes only when active validation is needed
6. Route to one core skill when the next step is clear
7. Recommend the next safe action

Expand branch comparison to other local or `origin/*` branches only when the user asks for broader triage or when primary comparisons show unresolved divergence.

## Output Shape
1. Selected core skill
2. Recent failure notes when present
3. Safety
4. Branch matrix
5. Env state
6. Connection checks
7. Debug root cause when needed
8. Production readiness
9. Next safe action
