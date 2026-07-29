---
name: cig-pipeline
description: >-
  End-to-end pipeline for NiCE WFM Customer Integration Guides (CIGs): draft →
  gate-review → revise loop → human approval. Use whenever someone wants to
  create, produce, run, or approve a CIG through the full process — e.g.
  "create a CIG for <vendor>", "draft and review an integration guide", "run
  the CIG pipeline", "get this CIG ready for publishing", "approve this CIG",
  "review and sign off this integration guide". Orchestrates two existing
  skills — nice-cig-writer (draft/revise) and cig-reviewer (publish gate +
  scorecard) — looping until the gate passes, then hands a decision package to
  a human for final approval. It never publishes on its own.
---

# CIG Pipeline — draft → review → revise → human approval

You are the **pipeline conductor**. You do not write or grade the guide
yourself — you drive two specialist skills through three gates and enforce the
loop policy:

| Gate | Owner | Skill | Output |
|------|-------|-------|--------|
| **1 Draft** | Creator | `nice-cig-writer` (draft mode) | draft `.docx`, status = **Draft** |
| **2 Review** | Reviewer | `cig-reviewer` | verdict + per-section scorecard + findings + redlined `.docx` |
| **3 Approve** | Human | — | final sign-off + the "Published" flip |

Invoke the specialist skills with the **Skill** tool (`nice-cig-writer`,
`cig-reviewer`). Keep the run's audit trail with `scripts/run_state.py`.

## Locked policy (do not silently change)
- **Exit bar (Gate 2 → human):** PASS = **0 blockers AND 0 majors** from
  `cig-reviewer`. Minors are allowed through and become the human punch-list.
- **Max auto-revise rounds:** **3**. After the 3rd review that still isn't a
  PASS, stop looping and **ESCALATE** to the human with the remaining findings.
- **Auto-revise scope:** **mechanical only** — placeholders, leftover
  scaffolding, typos/punctuation, formatting/table hygiene, product-name and
  version-gate consistency. For **missing technical content or accuracy gaps,
  never invent vendor facts** — collect them as explicit questions for the
  human (`nice-cig-writer` has the same no-fabrication rule; respect it).
- **Never set Distribution Status = Published.** That is the human's decision
  at Gate 3. Drafts and revisions stay status = Draft.

## Entry points (detect from the prompt)
- **CREATE** — "create/draft a CIG for X", or the user supplies raw notes /
  Jira / design docs. → start at **Gate 1**.
- **REVIEW / APPROVE** — "review / approve / gate this CIG" + an existing
  draft `.docx` (or PDF). → skip Gate 1, start at **Gate 2**. (A PDF gets a
  content-only review — redlines need the `.docx`; say so.)

If it's ambiguous which one, ask — don't assume.

## Procedure

Set `RUN=<scratch>/cig_run_<slug>.json` and initialise:
```bash
python3 scripts/run_state.py init "$RUN" --guide "<path-or-name>" --mode create|review --max-rounds 3
```

### Gate 1 — Draft (CREATE entry only)
1. Gather the inputs `nice-cig-writer` needs (vendor/integration name, ACD
   versions, target WFM release, media types/channels, historical vs real-time,
   connectivity, known limitations, diagram availability). Pass through
   whatever the user gave (rough notes, Jira tickets, design docs). If required
   facts are missing, `nice-cig-writer` will leave writer-instruction text in
   place — that's expected; those gaps surface at Gate 2 and go to the human.
2. **Invoke `nice-cig-writer` in draft mode.** Capture the output `.docx` path
   as `$GUIDE`. Confirm Distribution Status = **Draft**.

### Gate 2 — Review (every round)
1. **Invoke `cig-reviewer` on `$GUIDE`.** Get its three deliverables: the
   `GATE_REVIEW.md` (verdict + per-section scorecard + findings), the redlined
   `.docx` (margin comments), and the `_REVIEW.docx` **review copy** (verdict
   banner + blockers table on page 1). Surface the review copy to the human at
   Gate 3 — it's the at-a-glance artifact.
2. Count blockers `B`, majors `M`, minors `m`. Record the round:
   ```bash
   python3 scripts/run_state.py record "$RUN" --round <N> \
     --verdict READY|NOT_READY --blockers B --majors M --minors m \
     --report "<...GATE_REVIEW.md>" --redlined "<..._redlined.docx>" --action "<what happened>"
   ```
   The command prints the decision: **PASS | CONTINUE | ESCALATE**.

### Loop — Revise (only on CONTINUE)
1. Split the reviewer's findings into **mechanical** (auto-fixable) vs
   **content/accuracy** (needs human facts).
2. **Invoke `nice-cig-writer` to revise `$GUIDE`**, applying *only* the
   mechanical fixes (you may hand it the redlined `.docx` and the findings
   list). For each content/accuracy gap, add a question to the human queue —
   do **not** fabricate. Keep status = Draft.
3. Go back to **Gate 2** with the revised `$GUIDE`, incrementing the round.
   Never exceed `max_rounds` — the helper enforces it (returns ESCALATE).

### Gate 3 — Human approval (on PASS or ESCALATE)
Assemble a **decision package** and hand it to the human — do not publish:
- **Recommendation:** `READY FOR PUBLISH` (PASS) or `NEEDS HUMAN DECISION`
  (ESCALATE), with the reason.
- **Scorecard** from the final review + blocker/major/minor counts.
- **Open punch-list:** remaining minors (and any majors, if ESCALATE).
- **Content questions:** every accuracy/content gap the loop refused to
  invent — the specific facts the human must supply.
- **Artifacts:** final draft `.docx`, latest redlined `.docx`, the gate report,
  and the round log (`run_state.py show "$RUN"`).
- **Next step:** the human reviews, supplies any missing facts / accepts
  redlines, and — only they — sets Distribution Status = Published.

Then stop. The pipeline's job ends at the human's desk.

## Report back (chat)
Give a tight summary: entry point taken, how many rounds ran, the final
verdict, what auto-revise fixed, what still needs the human (punch-list +
content questions), and where the artifacts are. Point to the run log for
detail.

## Guardrails
- One scoring authority: **`cig-reviewer`** owns the gate verdict/score.
  (`nice-cig-writer` has an audit mode too, but don't use it for the gate —
  that would be two rulebooks.)
- Don't loop forever and don't hide truncation: if you ESCALATE at the cap,
  say so plainly with the still-open findings.
- Don't rewrite the customer's `.docx` outside the writer/reviewer skills, and
  never flip to Published.
- If a specialist skill isn't available in the current surface, say so and fall
  back to running the available gate manually rather than pretending.
