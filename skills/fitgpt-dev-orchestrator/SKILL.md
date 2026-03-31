---
name: fitgpt-dev-orchestrator
description: Run FitGPT with one repeatable operating procedure every session across macOS and Windows. Use when inspecting repo safety, comparing backend-features against dieuni, main, and all other branches, validating local versus production API routing, starting local services, debugging integration failures, and recommending the next safe move without destructive Git actions.
---

# FitGPT Dev Orchestrator

## Purpose
Run the FitGPT repository with one repeatable operating procedure every session.
Use this skill to inspect repo safety, compare branches, validate local versus production API routing, start local services, debug integration failures, and recommend the next safe move.

## Non-Negotiable Rules
- Treat `dieuni` as strictly read-only. Never modify it, never merge into it, and never switch to it automatically.
- Never commit, push, merge, reset, rebase, force-push, or delete branches unless the user explicitly asks.
- Never overwrite `.env`, `.env.local`, or `.env.production` silently. Create missing files only when the user explicitly wants that environment configured.
- Validate locally before recommending any production or Render-facing change.
- Switch frontend API targets by environment variables only. Do not edit runtime logic merely to move between local and production.
- Do not run `scripts/bootstrap.ps1` or `scripts/bootstrap.sh` automatically in FitGPT. Those scripts hard-switch to `dieuni`, which violates this orchestrator branch-safety contract.

## Required Internal Skill Chain
Every invocation of this skill must load and apply these skills in this order:

1. `Git Preflight`
2. `Codebase Auditor`
3. `FitGPT Stack Engineer`
4. `Bug Hunter`
5. `Senior Full-Stack Engineer`

Resolve dependency skills from:
- `$CODEX_HOME/skills` when `CODEX_HOME` is set.
- `~/.codex/skills` on macOS when `CODEX_HOME` is unset.
- `%USERPROFILE%\.codex\skills` on Windows when `CODEX_HOME` is unset.

Apply them like this:
- Use `Git Preflight` to determine whether fetch and pull are safe, and to block risky Git moves early.
- Use `Codebase Auditor` to map architecture, identify integration and deployment risks, and frame branch and env findings in system terms.
- Use `FitGPT Stack Engineer` to validate FastAPI, React, Android, auth, and API-contract behavior as one connected system.
- Use `Bug Hunter` whenever connection checks, startup, auth, or cross-layer behavior fails.
- Use `Senior Full-Stack Engineer` before proposing or applying code changes so fixes stay minimal, production-ready, and aligned with repo boundaries.

If any dependency skill is missing:
- Say it explicitly.
- Continue with equivalent behavior from this skill.
- Do not claim the missing skill ran.

## Core Tooling
This skill ships with one helper script:
- `scripts/fitgpt_orchestrator.py`

Use it for:
- Repo and branch analysis.
- Safe branch-diff summaries.
- Local versus production environment inspection.
- Local and production API probes.
- Detached backend and frontend startup through existing repo run scripts when available.

Prefer the helper script over ad hoc Git chains whenever the standard FitGPT report shape is needed.

## Phase 1 - Repo Safety
Resolve FitGPT repo root from current directory or provided path.
Confirm repo contains `backend/`, `web/`, and `scripts/`.
Run read-only safety snapshot first.

Windows:
```powershell
python "$env:USERPROFILE\.codex\skills\fitgpt-dev-orchestrator\scripts\fitgpt_orchestrator.py" report --repo "<repo-root>" --mode auto
```

macOS:
```bash
python3 ~/.codex/skills/fitgpt-dev-orchestrator/scripts/fitgpt_orchestrator.py report --repo "<repo-root>" --mode auto
```

Invoke `Git Preflight` logic immediately after snapshot.
Only fetch remote refs when tracked files are clean. When safe, rerun with `--fetch`.
Stop and wait if Git safety blocks progress. Do not bypass stop conditions with alternative destructive commands.

## Phase 2 - Branch Analysis
Always compare backend branch against:
- `backend-features`
- `dieuni`
- `main` when present
- Every other local or `origin/*` branch that resolves cleanly

Required report fields:
- Current branch
- Upstream tracking state
- Ahead/behind counts
- Commits missing from `backend-features`
- Commits unique to `backend-features`
- Changed-file summary for `dieuni` and `main`
- Recommended safe merge strategy

Use helper script output as primary branch matrix.
When deeper review is needed, run read-only:
```bash
git -C "<repo-root>" diff --stat <base-ref>..<other-ref>
git -C "<repo-root>" log --left-right --graph --cherry-pick --oneline <base-ref>...<other-ref>
```

Branch rules:
- `backend-features` is safe update target.
- `dieuni` is comparison-only.
- Prefer cherry-pick or disposable integration branch when histories diverge.
- Never recommend direct merge into `dieuni`.

## Phase 3 - Local Env Setup
If active development is requested, start local services only after Phases 1 and 2 complete.
Use helper script to launch detached services, preferring repo run scripts:
- `scripts/run-backend.ps1` or `scripts/run-backend.sh`
- `scripts/run-web.ps1` or `scripts/run-web.sh`
- Safe fallback only when those scripts are missing

Windows:
```powershell
python "$env:USERPROFILE\.codex\skills\fitgpt-dev-orchestrator\scripts\fitgpt_orchestrator.py" start --repo "<repo-root>" --timeout 120
```

macOS:
```bash
python3 ~/.codex/skills/fitgpt-dev-orchestrator/scripts/fitgpt_orchestrator.py start --repo "<repo-root>" --timeout 120
```

## Phase 4 - Environment Detection
Always inspect before discussing routing:
- `web/.env.local`
- `web/.env.production`
- `backend/.env`
- `backend/.env.example`
- `web/src/api/apiFetch.js`
- `backend/app/main.py` CORS configuration

Determine:
- Whether frontend points to localhost or `127.0.0.1`.
- Whether Render URL is explicitly configured.
- Whether production still depends on hardcoded source fallback.
- Whether backend CORS allows expected frontend origin.

Report one state:
- `LOCAL`
- `PRODUCTION`
- `MIXED`
- `UNKNOWN`

`MIXED` means env files and source fallback disagree, or frontend target disagrees with backend/CORS assumptions.

## Phase 5 - Safe Switching
Switching rules:
- Use `REACT_APP_API_BASE_URL` in `web/.env.local` for local mode.
- Use `REACT_APP_API_BASE_URL` in `web/.env.production` for production mode.
- Never edit `web/src/api/apiFetch.js` only to switch targets.
- If `web/.env.production` is missing and user explicitly requests production wiring, create only that file.
- Preserve existing secrets and unrelated keys.
- If hardcoded fallback remains in `apiFetch.js`, report it as risk unless user asked for env hardening edits.

## Phase 6 - Connection Validation
Always validate both configuration and reachability in order:
1. Confirm frontend API base URL resolves to intended target.
2. Probe backend root for selected mode.
3. Confirm local mode allows `http://localhost:3000` or `http://127.0.0.1:3000` through backend CORS.
4. If local services are running, probe frontend root on `http://127.0.0.1:3000`.

Use helper script probes:

Windows:
```powershell
python "$env:USERPROFILE\.codex\skills\fitgpt-dev-orchestrator\scripts\fitgpt_orchestrator.py" report --repo "<repo-root>" --mode auto --fetch
python "$env:USERPROFILE\.codex\skills\fitgpt-dev-orchestrator\scripts\fitgpt_orchestrator.py" start --repo "<repo-root>" --check-only
```

macOS:
```bash
python3 ~/.codex/skills/fitgpt-dev-orchestrator/scripts/fitgpt_orchestrator.py report --repo "<repo-root>" --mode auto --fetch
python3 ~/.codex/skills/fitgpt-dev-orchestrator/scripts/fitgpt_orchestrator.py start --repo "<repo-root>" --check-only
```

Treat failed probes as debugging tasks, never as justification for guessing.

## Phase 7 - Debugging
When validation fails, immediately switch into Bug Hunter mode while keeping orchestrator context.
Trace failures across:
- `web/src/api/apiFetch.js`
- Frontend env files
- `backend/.env`
- FastAPI startup and route availability
- Auth token or cookie expectations
- CORS in `backend/app/main.py`
- Render URL mismatches
- Dependency or venv issues in startup

Always state:
- Problem summary
- Root cause
- Exact file or layer
- Smallest safe fix

Never rewrite large sections for env or contract mismatch.

## Phase 8 - Production Readiness
Run Codebase Auditor and Senior Full-Stack Engineer checks before recommending release steps.
Validate:
- Frontend production URL target is explicit.
- Backend Render URL is reachable.
- No localhost leakage in production env files.
- Auth strategy matches deployed backend behavior.
- CORS is broad enough for deployed frontend and no broader than needed.
- Missing third-party env keys are clearly called out.

Never deploy, push, or mutate Render or Vercel state automatically from this skill.

## Phase 9 - Workflow Standardization
Every session should output in this order:
1. Safety
2. Branch Matrix
3. Env State
4. Connection Checks
5. Debug Root Cause when needed
6. Production Readiness
7. Next Safe Action

Keep output terse, factual, and actionable.

## Phase 10 - Automation
Use helper script instead of rebuilding orchestration each session.

Supported actions:
- `report`: read-only repo, branch, env, and probe analysis
- `start`: detached local backend and frontend startup with health checks
- `start --check-only`: probe running services without relaunching

## Merge Strategy Rules
Recommend only safe strategies:
- If `backend-features` is behind another branch and has no unique commits, recommend fast-forward only when target is not `dieuni`.
- If histories diverge, recommend one of:
  - Review and cherry-pick selected commits into `backend-features`.
  - Merge into disposable integration branch first.
  - Re-run tests locally before any merge request.
- If `dieuni` contains needed frontend work, recommend cherry-picks or temporary integration branch.
- If fetch was blocked by local changes, explicitly label ahead/behind counts as potentially stale.

## Stop Conditions
Stop and wait when any are true:
- Tracked local changes block safe fetch or pull.
- Repo is detached HEAD.
- `origin` is missing or clearly wrong.
- Target env file would need overwriting without explicit request.
- User asks to modify `dieuni`.
- Branch comparison divergence needs explicit human decision.

## Output Contract
Use this exact response shape:

`Safety`
- repo root
- active branch
- cleanliness
- origin
- upstream state
- Git blockers

`Branch Matrix`
- `backend-features` versus `dieuni`
- `backend-features` versus `main` when available
- `backend-features` versus other branches
- ahead/behind counts
- missing commits
- changed-file summary
- recommended safe strategy

`Env State`
- local frontend API URL
- production frontend API URL
- source fallback URL
- backend frontend URL and CORS notes
- selected mode
- env risks

`Connection Checks`
- local backend probe
- production backend probe when known
- local frontend probe when requested

`Debug Root Cause`
- include only when a failure exists

`Production Readiness`
- release blockers
- env gaps
- config improvements

`Next Safe Action`
- one short paragraph or short flat list

## Implementation Notes
- Favor helper script for repeated analysis.
- Favor existing repo run scripts for startup.
- Favor small explicit env edits over source routing changes.
- Favor read-only Git inspection over branch switching.
- Favor minimal fixes grounded in current architecture.

## Helper Command Reference
macOS:
```bash
python3 ~/.codex/skills/fitgpt-dev-orchestrator/scripts/fitgpt_orchestrator.py start --repo "<repo-root>" --timeout 120
python3 ~/.codex/skills/fitgpt-dev-orchestrator/scripts/fitgpt_orchestrator.py report --repo "<repo-root>" --mode auto
```

Windows:
```powershell
python "$env:USERPROFILE\.codex\skills\fitgpt-dev-orchestrator\scripts\fitgpt_orchestrator.py" start --repo "<repo-root>" --timeout 120
python "$env:USERPROFILE\.codex\skills\fitgpt-dev-orchestrator\scripts\fitgpt_orchestrator.py" report --repo "<repo-root>" --mode auto
```
