#!/usr/bin/env bash
# Installs exported custom Codex skills into ~/.codex/skills on macOS/Linux.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/skills"
TARGET_DIR="$HOME/.codex/skills"
GROUP_DIR="$SCRIPT_DIR/groups"

mkdir -p "$TARGET_DIR"

collect_skills() {
  if [ "$#" -eq 0 ]; then
    find "$SOURCE_DIR" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort
    return
  fi

  for arg in "$@"; do
    case "$arg" in
      core|utility)
        cat "$GROUP_DIR/$arg.txt"
        ;;
      *)
        printf '%s\n' "$arg"
        ;;
    esac
  done
}

collect_skills "$@" | awk 'NF && !seen[$0]++' | while IFS= read -r skill_name; do
  skill_dir="$SOURCE_DIR/$skill_name"
  target_path="$TARGET_DIR/$skill_name"

  if [ ! -d "$skill_dir" ]; then
    echo "Skipping unknown skill: $skill_name" >&2
    continue
  fi

  rm -rf "$target_path"
  cp -R "$skill_dir" "$target_path"
  echo "Installed: $skill_name"
done

echo "Selected custom skills installed to $TARGET_DIR"
