---
name: fitgpt-stack-engineer
description: Build, review, debug, and improve full-stack mobile apps that use a FastAPI backend and a Jetpack Compose Android client. Use when Codex must implement or analyze end-to-end features across FastAPI, SQLAlchemy, JWT auth, REST APIs, Pydantic schemas, Retrofit networking, MVVM, DataStore token handling, and Compose UI while keeping code secure, simple, and maintainable.
---

# FitGPT Stack Engineer

## Skill Group
Core system skill

## Purpose
Handle FitGPT work that spans the FastAPI backend and Jetpack Compose Android client as one connected system.

## Modes
### Read / Analyze
- Identify which FitGPT layers are involved: backend, API, auth, networking, Android state, or UI.
- Check existing models, endpoints, repositories, ViewModels, and screens before proposing changes.
- Validate assumptions across API contracts and client models.

### Execution
- Change only the affected layers.
- Keep backend, API, and Android behavior aligned end to end.
- Preserve existing project patterns for FastAPI, SQLAlchemy, Retrofit, MVVM, and Compose.

## Run Logging
Record one Markdown log per run:
```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export SKILL_LOGGER="$CODEX_HOME/skills/fitgpt-dev-orchestrator/scripts/skill_run_log.py"
RUN_LOG=$(python3 "$SKILL_LOGGER" --skill "fitgpt-stack-engineer" --action "implement <fitgpt-change>" --status started)
# ...run the implementation...
python3 "$SKILL_LOGGER" --skill "fitgpt-stack-engineer" --action "implement <fitgpt-change>" --status success --log-file "$RUN_LOG"
# on failure: use --status failure
```

## Coverage
- FastAPI endpoints, validation, and auth
- SQLAlchemy models and persistence
- REST request and response contracts
- Retrofit networking and token handling
- ViewModel, repository, and Compose UI state

## Working Rules
- Prefer existing services and abstractions over new architecture.
- Keep auth handling secure and explicit.
- Handle network errors, empty responses, invalid input, duplicate data, expired tokens, and server failures.
- Add comments only for non-obvious design intent.

## Output Shape
1. Feature or bug overview
2. Affected FitGPT layers
3. Implementation plan
4. Relevant backend and Android changes
5. Edge cases handled
6. Testing steps
