#!/usr/bin/env bash
# SessionStart hook (matcher: compact): after a compaction, inject the saved
# checkpoint back into the fresh context so work resumes without starting over.
set -euo pipefail

input="$(cat)"
proj="$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null || true)"
proj="${proj:-${CLAUDE_PROJECT_DIR:-$PWD}}"

checkpoint="$proj/.claude/checkpoints/CONTEXT-CHECKPOINT.md"

if [ -f "$checkpoint" ]; then
  jq -n --rawfile c "$checkpoint" \
    '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: ("Context restored from the pre-compaction checkpoint. Resume from this — do not start fresh:\n\n" + $c)}}'
fi
