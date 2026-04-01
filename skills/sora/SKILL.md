---
name: "sora"
description: "Use when the user asks to generate, edit, extend, poll, list, download, or delete Sora videos, create reusable non-human Sora character references, or run local multi-video queues via the bundled CLI (`scripts/sora.py`); includes requests like: (i) generate AI video, (ii) edit this Sora clip, (iii) extend this video, (iv) create a character reference, (v) download video/thumbnail/spritesheet, and (vi) Sora batch planning; requires `OPENAI_API_KEY` and Sora API access."
---

# Sora Video Generation Skill

## Skill Group
Utility skill

## Purpose
Plan and run focused Sora video workflows through the bundled CLI.

## Modes
### Read / Analyze
- Decide whether the task is create, create-character, edit, extend, status, download, or batch planning.
- Collect the required inputs: prompt, model, size, duration, references, and IDs.
- Confirm auth, model limits, and any content-policy blockers before live API work.

### Execution
- Use `scripts/sora.py` with sensible defaults.
- Prefer targeted prompt iteration and one clear change per step.
- Poll async jobs until terminal state and download assets before URLs expire.

## Run Logging
Record one Markdown log per run:
```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export SKILL_LOGGER="$CODEX_HOME/skills/fitgpt-dev-orchestrator/scripts/skill_run_log.py"
RUN_LOG=$(python3 "$SKILL_LOGGER" --skill "sora" --action "run <video-task>" --status started)
# ...run the Sora workflow...
python3 "$SKILL_LOGGER" --skill "sora" --action "run <video-task>" --status success --log-file "$RUN_LOG"
# on failure: use --status failure
```

## Workflow
1. Choose the correct Sora action
2. Gather required inputs
3. Prefer CLI augmentation flags unless a structured prompt file is already prepared
4. Run the CLI
5. Poll or inspect status
6. Download or manage assets as requested

## Defaults And Rules
- Default model: `sora-2`
- Default size: `1280x720`
- Default duration: `4`
- Require `OPENAI_API_KEY` for live API calls
- Prefer the bundled CLI and do not modify it unless the user asks

## Guardrails
- Only content suitable for audiences under 18
- No copyrighted characters or music
- No real people
- Character uploads are for non-human subjects only

## References
- `references/cli.md`
- `references/video-api.md`
- `references/prompting.md`
- `references/troubleshooting.md`
