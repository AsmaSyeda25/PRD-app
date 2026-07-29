# Writer ↔ Reviewer rulebook alignment

The pipeline chains `nice-cig-writer` (Creator) and `cig-reviewer` (Gate). They
must share **one** structural rulebook or the loop sends mixed signals. This
note records the reconciliation.

## Decision
**Customer Responsibilities is its own chapter — Chapter 2**, between
Introduction and Overview.

## Canonical 7-chapter order (both skills)
1. Introduction (+ Document Revision History)
2. **Customer Responsibilities**
3. Overview (Media Types / Channels / Data Types, Intervals, Historical & Real-Time, Vendor Versions)
4. Technical Solution (Architecture + diagram, Protocol Summary, Data Retrieval)
5. Historical Integration (Media Types & Classifications, Contact Data Pegging, Data Requirements → Queue / Agent Queue / Agent System Data, Re-posting)
6. Real-Time Integration (Data Mapping, Data Constraints, Agent Activity sections)
7. Restrictions and Limitations

## What changed
- **`cig-reviewer`** — already had Customer Responsibilities as its own chapter
  in `reference/template-structure.json`; **no structural change needed**. Added
  a "Canonical structure decisions" note to `reference/rubric.md` so it isn't
  reverted.
- **`nice-cig-writer`** (lives in `~/.claude/skills/`, **outside this repo**) —
  edited to match:
  - Moved **Customer Responsibilities** out of Chapter 3 (Technical Solution)
    into its own **Chapter 2**; renumbered Overview→3, Technical Solution→4,
    Historical→5, Real-Time→6, Restrictions→7.
  - Audit-mode checklist: "all 6 chapters" → "all 7 chapters"; "Customer
    Responsibilities listed explicitly in Chapter 3" → "…as its own Chapter 2".
  - "Known failure patterns": the chapter-numbering-drift note no longer calls
    Customer-Responsibilities-as-a-chapter a defect (it's now correct); the
    generic TOC-vs-body check is kept.

## ⚠️ Sync note
`nice-cig-writer` is a Cowork/user-level skill, so this repo does **not** carry
its source and the branch push does **not** update it. The edit above was
applied to the live session copy; to make it permanent, apply the same change
to the `nice-cig-writer` skill in Cowork. If the two ever diverge again, this
file plus `cig-reviewer/reference/template-structure.json` are the source of
truth for the intended structure.
