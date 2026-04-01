#!/usr/bin/env python3
"""Install selected custom Codex skills from this repository into ~/.codex/skills."""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path


def resolve_target_root() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home).expanduser() / "skills"
    return Path.home() / ".codex" / "skills"


def load_manifest(repo_root: Path) -> dict:
    manifest_path = repo_root / "manifest.json"
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def collect_requested(manifest: dict, args: list[str]) -> list[str]:
    if not args:
        return sorted(manifest["skills"].keys())

    selected: list[str] = []
    for arg in args:
        if arg in manifest["groups"]:
            for skill in manifest["groups"][arg]:
                if skill not in selected:
                    selected.append(skill)
            continue
        if arg in manifest["skills"] and arg not in selected:
            selected.append(arg)
            continue
        print(f"Skipping unknown skill or group: {arg}", file=sys.stderr)
    return selected


def copy_skill(repo_root: Path, skill_name: str, manifest: dict, target_root: Path) -> None:
    source_rel = manifest["skills"][skill_name]["path"]
    source = repo_root / source_rel
    target = target_root / skill_name
    backup = target_root / f".backup-{skill_name}"

    if not source.exists():
        raise FileNotFoundError(f"Missing source folder for skill '{skill_name}': {source}")

    target_root.mkdir(parents=True, exist_ok=True)

    if backup.exists():
        shutil.rmtree(backup)
    if target.exists():
        shutil.move(str(target), str(backup))

    try:
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)
        if backup.exists():
            shutil.rmtree(backup)
        print(f"Installed: {skill_name}")
    except Exception:
        if target.exists():
            shutil.rmtree(target)
        if backup.exists():
            backup.rename(target)
        raise


def main() -> int:
    repo_root = Path(__file__).resolve().parent
    manifest = load_manifest(repo_root)
    requested = collect_requested(manifest, sys.argv[1:])
    target_root = resolve_target_root()

    if not requested:
        print("No valid skills requested.", file=sys.stderr)
        return 1

    for skill_name in requested:
        copy_skill(repo_root, skill_name, manifest, target_root)

    print(f"Selected custom skills installed to {target_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
