---
name: git-preflight
description: Conservative Git pre-flight safety procedure used before any development work. Use when validating repository readiness, branch safety, local state cleanliness, origin sync status, and teammate branch ownership while preventing accidental overwrites, unsafe pulls, merge commits, and work on protected branches.
---

# Git Preflight Safety Checklist

## Skill Group
Core system skill

## Purpose
Run a read-first Git safety check before development work or sync operations.

## Modes
### Read / Analyze
- Confirm the directory is a Git repository.
- Identify the active branch and tracking state.
- Inspect local changes before any network or branch action.
- Report blockers and stop when the state is unsafe.

### Execution
- Only run safe inspection and sync commands that fit preflight.
- Fetch and `pull --ff-only` only when the working tree is clean and the task calls for sync validation.
- Do not clone, commit, push, merge, rebase, reset, stash, or switch branches unless the user explicitly asks.

## Run Logging
Record one Markdown log per run:
```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export SKILL_LOGGER="$CODEX_HOME/skills/fitgpt-dev-orchestrator/scripts/skill_run_log.py"
RUN_LOG=$(python3 "$SKILL_LOGGER" --skill "git-preflight" --action "check <repo-state>" --status started)
# ...run the preflight...
python3 "$SKILL_LOGGER" --skill "git-preflight" --action "check <repo-state>" --status success --log-file "$RUN_LOG"
# on failure: use --status failure
```

## Workflow
1. Validate repository and `origin`
2. Identify the current branch
3. Inspect local state with `git status`
4. If clean and relevant, run `git fetch origin`
5. If still safe and relevant, run `git pull --ff-only origin <current-branch>`
6. Confirm post-sync readiness
7. Add any known branch ownership warning

## Stop Conditions
- Not a Git repository
- Missing or wrong `origin`
- Detached HEAD
- Modified, staged, or untracked files
- Diverged history or non-fast-forward pull
- Any action that would require a destructive or history-rewriting command

## FitGPT Ownership Rule
- If branch is `dieuni`, warn that it is comparison-only and should not be modified unless explicitly required.

## Output Shape
1. Repository validation result
2. Active branch and tracking state
3. Local state result
4. Sync result
5. Safety note
6. Final readiness statement
