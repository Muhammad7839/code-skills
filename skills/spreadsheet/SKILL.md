---
name: "spreadsheet"
description: "Use when tasks involve creating, editing, analyzing, or formatting spreadsheets (`.xlsx`, `.csv`, `.tsv`) with formula-aware workflows, cached recalculation, and visual review."
---

# Spreadsheet Skill

## Skill Group
Utility skill

## Purpose
Create, edit, analyze, or format spreadsheets without breaking formulas, references, or layout.

## Modes
### Read / Analyze
- Confirm file type and task: create, edit, analyze, or visualize.
- Inspect formulas, formatting, and sheet structure before editing.
- Render or recalculate when available if layout or cached values matter.

### Execution
- Use `openpyxl` for `.xlsx` structure and formatting.
- Use `pandas` for tabular analysis and CSV or TSV workflows.
- Preserve formulas and formatting unless the user asks for redesign.

## Run Logging
Record one Markdown log per run:
```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export SKILL_LOGGER="$CODEX_HOME/skills/fitgpt-dev-orchestrator/scripts/skill_run_log.py"
RUN_LOG=$(python3 "$SKILL_LOGGER" --skill "spreadsheet" --action "process <sheet-task>" --status started)
# ...run the spreadsheet task...
python3 "$SKILL_LOGGER" --skill "spreadsheet" --action "process <sheet-task>" --status success --log-file "$RUN_LOG"
# on failure: use --status failure
```

## Workflow
1. Identify workbook type and expected output.
2. Inspect existing formulas, formats, and dependencies.
3. Make the requested edit or analysis with `openpyxl` or `pandas`.
4. Recalculate and render when tooling is available.
5. Check formulas, formatting, and readability before delivery.

## Conventions
- Use `tmp/spreadsheets/` for intermediate files.
- Write final artifacts under `output/spreadsheet/` in this repo.
- Keep filenames stable and descriptive.

## Rules
- Use formulas for derived values instead of hardcoding results.
- Keep formulas legible and avoid volatile or unsupported features unless required.
- Preserve existing formatting exactly when editing a styled workbook.
- Use sensible number, date, percent, and currency formats when creating a new workbook.
