#!/usr/bin/env bash
# Installs all exported custom Codex skills into ~/.codex/skills on macOS/Linux.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/skills"
TARGET_DIR="$HOME/.codex/skills"

mkdir -p "$TARGET_DIR"

find "$SOURCE_DIR" -mindepth 1 -maxdepth 1 -type d | while IFS= read -r skill_dir; do
  skill_name="$(basename "$skill_dir")"
  target_path="$TARGET_DIR/$skill_name"

  rm -rf "$target_path"
  cp -R "$skill_dir" "$target_path"
  echo "Installed: $skill_name"
done

echo "All custom skills installed to $TARGET_DIR"
