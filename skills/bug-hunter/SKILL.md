---
name: bug-hunter
description: Debug complex software systems by tracing failures across backend services, APIs, databases, frontend apps, Android clients, and integrations. Use when Codex should investigate bugs, crashes, edge cases, race conditions, logic errors, and cross-layer mismatches, then recommend minimal safe fixes with clear root-cause reasoning.
---

# Bug Hunter

## Skill Group
Core system skill

## Purpose
Find the root cause of a failure and guide the smallest reliable fix.

## Modes
### Read / Analyze
- Read code, logs, stack traces, and failure reports carefully.
- Trace the failure path across files and layers before proposing changes.
- Explain the root cause with evidence.

### Execution
- Apply or recommend the smallest safe fix.
- Add only the guard conditions, validation, or logging needed to close the bug.
- Avoid broad refactors unless the bug cannot be fixed safely without them.

## Run Logging
Record one Markdown log per run:
```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export SKILL_LOGGER="$CODEX_HOME/skills/fitgpt-dev-orchestrator/scripts/skill_run_log.py"
RUN_LOG=$(python3 "$SKILL_LOGGER" --skill "bug-hunter" --action "debug <target>" --status started)
# ...run the investigation...
python3 "$SKILL_LOGGER" --skill "bug-hunter" --action "debug <target>" --status success --log-file "$RUN_LOG"
# on failure: use --status failure
```

## Investigation Focus
- Null references and unhandled exceptions
- Invalid or unexpected data
- Async, concurrency, and state-sync issues
- Network, timeout, and auth failures
- Cross-layer contract mismatches
- Missing error handling and weak validation

## Working Rules
- Do not guess causes without code evidence.
- Prefer a direct fix over defensive churn across unrelated files.
- Recommend focused logs only when diagnosis remains unclear.

## Output Shape
1. Problem summary
2. Root cause analysis
3. Where the bug occurs
4. Fix strategy
5. Implementation
6. Edge cases covered
7. Additional improvements
