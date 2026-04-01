---
name: codebase-auditor
description: Perform full-repository engineering audits before development begins, covering architecture, backend services, APIs, databases, Android/frontend clients, and integrations. Use when Codex should review an existing codebase to identify security issues, integration bugs, reliability risks, edge cases, maintainability problems, and architectural weaknesses without rewriting the system.
---

# Codebase Auditor

## Skill Group
Core system skill

## Purpose
Audit an existing repository and identify concrete engineering risks before more development happens.

## Modes
### Read / Analyze
- Map the repository structure and major subsystems.
- Trace key request and data flows across backend, clients, database, and integrations.
- Compare assumptions between layers and record risks with evidence.

### Execution
- Do not rewrite the system.
- Only produce findings, risk ranking, and practical recommendations unless the user explicitly asks for fixes.

## Run Logging
Record one Markdown log per run:
```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export SKILL_LOGGER="$CODEX_HOME/skills/fitgpt-dev-orchestrator/scripts/skill_run_log.py"
RUN_LOG=$(python3 "$SKILL_LOGGER" --skill "codebase-auditor" --action "audit <repo>" --status started)
# ...run the audit...
python3 "$SKILL_LOGGER" --skill "codebase-auditor" --action "audit <repo>" --status success --log-file "$RUN_LOG"
# on failure: use --status failure
```

## Audit Areas
- Backend services and business logic
- API routes, handlers, and contracts
- Database models and persistence
- Authentication and authorization
- Frontend and Android state handling
- Cross-layer integrations and external dependencies
- Maintainability and documentation gaps

## Review Rules
- Analyze only files that exist.
- Prefer concrete findings over generic advice.
- Focus on security, reliability, edge cases, integration mismatch, and maintainability.
- Recommend minimal-disruption improvements first.

## Output Shape
1. Repository overview
2. Key system components
3. Architecture observations
4. Issues found
5. Potential crash scenarios
6. Security concerns
7. Improvement recommendations
8. Risk summary
