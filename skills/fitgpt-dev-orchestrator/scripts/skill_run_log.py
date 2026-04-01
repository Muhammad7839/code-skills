#!/usr/bin/env python3
"""Record lightweight per-run skill logs in a readable Markdown file."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import re
import sys


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return normalized or "skill"


def resolve_codex_home() -> Path:
    return Path.home() / ".codex" if "CODEX_HOME" not in __import__("os").environ else Path(__import__("os").environ["CODEX_HOME"]).expanduser()


def build_log_path(codex_home: Path, skill: str) -> Path:
    now = datetime.now()
    log_dir = codex_home / "skill-logs" / now.strftime("%Y-%m-%d")
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / f"{now.strftime('%H%M%S')}-{slugify(skill)}.md"


def init_log(path: Path, skill: str, action: str, status: str, details: str | None) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z").strip()
    lines = [
        f"# Skill Run Log: {skill}",
        "",
        f"- Skill: `{skill}`",
        f"- Started: {now}",
        f"- Current status: `{status}`",
        "",
        "## Actions",
        "",
        f"- {now} | action=`{action}` | status=`{status}`" + (f" | details={details}" if details else ""),
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def update_log(path: Path, action: str, status: str, details: str | None) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z").strip()
    existing = path.read_text(encoding="utf-8")
    entry = f"- {now} | action=`{action}` | status=`{status}`" + (f" | details={details}" if details else "")

    if "## Actions" not in existing:
        existing = existing.rstrip() + "\n\n## Actions\n\n"

    updated = existing.rstrip() + "\n" + entry + "\n"
    updated = re.sub(r"- Current status: `[^`]+`", f"- Current status: `{status}`", updated, count=1)

    if status in {"success", "failure"}:
        if re.search(r"- Finished: .*", updated):
            updated = re.sub(r"- Finished: .*", f"- Finished: {now}", updated, count=1)
        else:
            updated = updated.replace("## Actions", f"- Finished: {now}\n\n## Actions", 1)

    path.write_text(updated, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record a skill run log entry.")
    parser.add_argument("--skill", required=True, help="Skill name.")
    parser.add_argument("--action", required=True, help="Short action summary.")
    parser.add_argument(
        "--status",
        required=True,
        choices=["started", "success", "failure"],
        help="Run status for this log entry.",
    )
    parser.add_argument("--details", help="Optional short details.")
    parser.add_argument("--log-file", help="Existing log file to append to.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    codex_home = resolve_codex_home()
    path = Path(args.log_file).expanduser() if args.log_file else build_log_path(codex_home, args.skill)

    try:
        if path.exists():
            update_log(path, args.action, args.status, args.details)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            init_log(path, args.skill, args.action, args.status, args.details)
        print(path)
        return 0
    except Exception as exc:  # pragma: no cover
        print(f"Failed to write skill log: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
