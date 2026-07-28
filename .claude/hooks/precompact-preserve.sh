#!/usr/bin/env bash
# PreCompact hook: preserve the context checkpoint before ANY compaction
# (manual or auto). A hook can't generate the intelligent summary itself — that
# is what the /checkpoint command does — so this backs up the existing
# checkpoint so it is never overwritten/lost, and warns if none exists yet.
set -euo pipefail

input="$(cat)"
trigger="$(printf '%s' "$input" | jq -r '.trigger // "unknown"' 2>/dev/null || echo unknown)"
proj="$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null || true)"
proj="${proj:-${CLAUDE_PROJECT_DIR:-$PWD}}"

checkpoint="$proj/.claude/checkpoints/CONTEXT-CHECKPOINT.md"
history="$proj/.claude/checkpoints/history"

if [ -f "$checkpoint" ]; then
  mkdir -p "$history"
  stamp="$(date +%Y%m%d-%H%M%S)"
  cp "$checkpoint" "$history/CONTEXT-CHECKPOINT-${trigger}-${stamp}.md" 2>/dev/null || true
  printf '%s\n' "{\"systemMessage\": \"✅ Checkpoint preserved before ${trigger} compaction (backup in .claude/checkpoints/history/). It will be re-loaded automatically after compaction.\", \"suppressOutput\": true}"
else
  printf '%s\n' "{\"systemMessage\": \"⚠️ Compacting (${trigger}) without a saved checkpoint — run /checkpoint first next time to guarantee no context is lost.\", \"suppressOutput\": true}"
fi
