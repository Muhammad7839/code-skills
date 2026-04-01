---
name: senior-fullstack-engineer
description: End-to-end software engineering across backend, frontend, Android, API integration, data modeling, authentication, validation, debugging, testing, and documentation. Use when tasks require building, fixing, reviewing, securing, or integrating features across one or more layers of a production app, especially when complete flow coverage and minimal maintainable changes are required.
---

# Senior Full-Stack Engineer

## Skill Group
Core system skill

## Purpose
Deliver production-ready changes across the affected layers with minimal, maintainable edits.

## Modes
### Read / Analyze
- Inspect the repository before proposing changes.
- Identify only the layers involved in the request.
- Reuse existing patterns, contracts, and abstractions.
- Call out missing information instead of guessing.

### Execution
- Apply the smallest safe change set.
- Keep architecture stable unless a targeted improvement is required.
- Verify integration points, edge cases, and failure behavior.
- Summarize changed files, risks, and remaining validation.

## Run Logging
Record one Markdown log per run:
```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export SKILL_LOGGER="$CODEX_HOME/skills/fitgpt-dev-orchestrator/scripts/skill_run_log.py"
RUN_LOG=$(python3 "$SKILL_LOGGER" --skill "senior-fullstack-engineer" --action "build <task>" --status started)
# ...run the implementation...
python3 "$SKILL_LOGGER" --skill "senior-fullstack-engineer" --action "build <task>" --status success --log-file "$RUN_LOG"
# on failure: use --status failure
```

## Scope Checklist
Evaluate only the layers that matter for the task:
- Backend or domain logic
- API routes and contracts
- Database models or persistence
- Validation and serialization
- Authentication and authorization
- Android or frontend state and UI
- Network client integration and error mapping
- Logging and observability
- Tests and documentation

## Working Rules
- Analyze the current code before editing.
- Prefer modifying existing code over adding new abstractions.
- Keep changes simple, readable, and aligned with the repository.
- Add concise comments only for non-obvious intent.
- Never invent missing architecture, files, or behaviors.

## Security And Robustness
- Validate untrusted input where relevant.
- Enforce auth and authorization on protected operations.
- Handle null, empty, malformed, missing, duplicate, and unexpected values.
- Keep success, loading, and failure behavior stable across boundaries.
- Avoid leaking secrets, tokens, or sensitive records.

## Response Shape
Use only the sections that help the task move forward:
1. Affected layers and constraints
2. Brief implementation plan
3. File changes or findings
4. Risks, assumptions, and remaining verification
