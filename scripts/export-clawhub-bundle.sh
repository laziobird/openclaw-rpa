#!/usr/bin/env bash
# Build a small folder for ClawHub drag-and-drop upload (excludes .git and runtime junk).
# Usage: ./scripts/export-clawhub-bundle.sh
# Output: ../openclaw-rpa-clawhub-upload/ (sibling of repo root by default)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${CLAWHUB_EXPORT_DIR:-$(dirname "$ROOT")/openclaw-rpa-clawhub-upload}"

echo "==> Source: $ROOT"
echo "==> Output: $OUT"
rm -rf "$OUT"
mkdir -p "$OUT"

# ClawHub validation: text-oriented bundle; exclude *.jsonl audit logs and large media.
rsync -a --delete \
  --exclude '.git/' \
  --exclude '__pycache__/' \
  --exclude '**/__pycache__/' \
  --exclude '.venv/' \
  --exclude 'venv/' \
  --exclude 'recorder_session/' \
  --exclude 'session.json' \
  --exclude 'config.json' \
  --exclude '.DS_Store' \
  --exclude '**/.DS_Store' \
  --exclude '*.pyc' \
  --exclude '.env' \
  --exclude '.env.*' \
  --exclude '*.mov' \
  --exclude '*.gif' \
  --exclude '*.mp4' \
  --exclude '*.jsonl' \
  "$ROOT/" "$OUT/"

# ClawHub rejects dotfiles named .gitignore; keep them in git, omit from upload bundle.
find "$OUT" -name '.gitignore' -delete
rmdir "$OUT/proofs" 2>/dev/null || true

# Ensure SKILL.md exists at bundle root
if [[ ! -f "$OUT/SKILL.md" ]]; then
  echo "ERROR: SKILL.md missing in bundle" >&2
  exit 1
fi

SIZE="$(du -sh "$OUT" | cut -f1)"
echo "==> Bundle size: $SIZE"
echo "==> Upload this folder in ClawHub: $OUT"
