#!/usr/bin/env bash
# Installs exported custom Codex skills into ~/.codex/skills on macOS/Linux.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/install.py" "$@"
