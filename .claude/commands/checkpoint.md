---
description: Capture a durable context checkpoint (plans, decisions, risks, next steps) before compacting, so no context is lost.
argument-hint: "[optional note, e.g. 'about to compact at 60%']"
allowed-tools: Read, Write, Bash(mkdir:*)
---

# Context Checkpoint (pre-compaction retention)

You are creating a **durable checkpoint** of this conversation so that context
survives `/compact` (or auto-compaction) without starting fresh. A compaction
summary can silently drop nuance; a file on disk cannot. This checkpoint is the
source of truth to re-read after compacting.

Optional note from the user for this checkpoint: **$ARGUMENTS**

## Step 1 — Extract, using THIS framework (omit a section only if truly empty)

Review the entire conversation so far and capture:

1. **Plans made** — any plan, design, or approach we agreed on or sketched.
   Include enough detail to resume execution (files, structure, sequence).
2. **Decisions & rationale** — what we decided and *why*, plus anything we
   explicitly rejected and why (so it isn't reopened later).
3. **Risks & mitigations** — known risks, blockers, or constraints, each paired
   with the mitigation / the way to move ahead. Include hard environment facts
   (e.g. network policy, auth limits) that change what's possible.
4. **Next steps** — concrete agreed next actions, in order. Mark who does what
   (user vs. Claude) and any input still needed from the user.

Also capture a short **Working context** block:
- What we are mid-way through right now (the live task).
- Key artifacts: file paths, URLs, branch name, credentials *approach* (never
  secrets themselves), and any commands/tools that mattered.
- Open questions awaiting the user's answer.

## Step 2 — Write the durable file

Run `mkdir -p .claude/checkpoints` first, then **overwrite**
`.claude/checkpoints/CONTEXT-CHECKPOINT.md` with the structured summary above.
Use clear `##` headings matching the framework so it's easy to re-read.
Start the file with the current date and the optional note.
Do NOT write secrets, tokens, or credentials into the file — describe the
*approach* only.

## Step 3 — Show the brief (in chat)

Print two short lists so the user can decide before compacting:

- **✅ Retained** — the high-value context now saved to the checkpoint file
  (the four framework sections + working context). This is what lets us resume
  without starting fresh.
- **🗜️ Safe to compact** — the low-value / recoverable material that does NOT
  need to survive verbatim (e.g. tool-call transcripts, exploratory dead-ends,
  re-derivable file listings, verbose command output). Say briefly why each is
  safe to drop.

## Step 4 — Hand off to compaction

Tell the user the checkpoint is saved and give them the exact next command,
including a retention instruction that mirrors this framework:

> Run: `/compact Preserve plans, decisions & rationale, risks & mitigations, and
> next steps. A full checkpoint is saved at .claude/checkpoints/CONTEXT-CHECKPOINT.md —
> re-read it after compacting.`

After compacting, the first thing to do is `Read
.claude/checkpoints/CONTEXT-CHECKPOINT.md` to restore full context.
