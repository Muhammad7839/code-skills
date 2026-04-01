---
name: "doc"
description: "Use when the task involves reading, creating, or editing `.docx` documents, especially when formatting or layout fidelity matters; prefer `python-docx` plus the bundled `scripts/render_docx.py` for visual checks."
---

# DOCX Skill

## Skill Group
Utility skill

## Purpose
Read, create, or edit `.docx` files while preserving layout quality.

## Modes
### Read / Analyze
- Inspect document structure, text, tables, and layout-sensitive sections.
- Prefer visual review when rendering is available.
- Call out layout risk if only text extraction is possible.

### Execution
- Use `python-docx` for structured edits and document creation.
- Re-render after meaningful changes when possible.
- Keep intermediate files organized and remove them after final approval.

## Run Logging
Record one Markdown log per run:
```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export SKILL_LOGGER="$CODEX_HOME/skills/fitgpt-dev-orchestrator/scripts/skill_run_log.py"
RUN_LOG=$(python3 "$SKILL_LOGGER" --skill "doc" --action "process <docx-task>" --status started)
# ...run the document task...
python3 "$SKILL_LOGGER" --skill "doc" --action "process <docx-task>" --status success --log-file "$RUN_LOG"
# on failure: use --status failure
```

## Workflow
1. Determine whether the task is review, edit, or creation.
2. Prefer rendering through `scripts/render_docx.py` or DOCX -> PDF -> PNG when tools are available.
3. Apply the requested document changes with `python-docx`.
4. Re-check layout and report any remaining fidelity risk.

## Conventions
- Use `tmp/docs/` for intermediate files.
- Write final artifacts under `output/doc/` in this repo.
- Keep filenames stable and descriptive.

## Tooling
- Python: `python-docx`, optionally `pdf2image`
- Rendering: `scripts/render_docx.py`, `soffice`, `pdftoppm`

## Quality Rules
- Preserve professional formatting and hierarchy.
- Avoid clipped text, broken tables, unreadable characters, and default-template styling.
- Use ASCII hyphens only.
