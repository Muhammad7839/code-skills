---
name: "pdf"
description: "Use when tasks involve reading, creating, or reviewing PDF files where rendering and layout matter; prefer visual checks by rendering pages (Poppler) and use Python tools such as `reportlab`, `pdfplumber`, and `pypdf` for generation and extraction."
---

# PDF Skill

## Skill Group
Utility skill

## Purpose
Read, create, or review PDFs with layout-aware validation.

## Modes
### Read / Analyze
- Inspect PDF content and rendering quality.
- Prefer page rendering over text extraction when layout matters.
- Use text extraction only for quick checks or fallback review.

### Execution
- Use `reportlab` for generation and `pdfplumber` or `pypdf` for extraction or inspection.
- Re-render updated PDFs before delivery when possible.
- Keep intermediate files organized and disposable.

## Run Logging
Record one Markdown log per run:
```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export SKILL_LOGGER="$CODEX_HOME/skills/fitgpt-dev-orchestrator/scripts/skill_run_log.py"
RUN_LOG=$(python3 "$SKILL_LOGGER" --skill "pdf" --action "process <pdf-task>" --status started)
# ...run the PDF task...
python3 "$SKILL_LOGGER" --skill "pdf" --action "process <pdf-task>" --status success --log-file "$RUN_LOG"
# on failure: use --status failure
```

## Workflow
1. Decide whether the task is review, edit, extraction, or generation.
2. Render pages with `pdftoppm` when visual fidelity matters.
3. Apply the requested PDF change with the appropriate Python tool.
4. Re-check the final rendering and note any remaining layout risk.

## Conventions
- Use `tmp/pdfs/` for intermediate files.
- Write final artifacts under `output/pdf/` in this repo.
- Keep filenames stable and descriptive.

## Quality Rules
- Preserve typography, spacing, margins, and legibility.
- Avoid clipped text, overlapping elements, broken tables, and unreadable glyphs.
- Use ASCII hyphens only.
