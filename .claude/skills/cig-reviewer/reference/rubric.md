# CIG Publish-Gate Rubric

The gate answers one question: **is this Customer Integration Guide ready to
publish?** Verdict is `READY` only if there are **zero Blockers**. Any Blocker →
`NOT READY`. Majors and Minors are reported but do not by themselves fail the
gate (they are the writer's punch-list).

Scope of this gate: **structure, format/hygiene, and internal consistency.**
It does **not** verify external technical accuracy (field mappings against the
IDD/vendor docs) — that is a future add-on. Never assert a mapping is
"correct" or "incorrect"; only flag when the document contradicts *itself*.

## Blocker  → fails the gate
- **Leftover placeholder** in prose: `<Integration name>` or any `<...>` fill-in
  token in body text.
  - *Not a blocker:* angle-bracket tokens that are spec/payload syntax, e.g.
    `<Logon ID> | <Agent State> | <Start Time> [ | <Start Date>]`, or tokens
    inside code/JSON/message-format blocks. Leave these alone.
- **Leftover template scaffolding**: `Example:` lines, instructional prompts
  ("Does the integration support…", "Indicate each…", "Provide specifics…",
  "The documentation team will create…", "(see IDD)", "High-level summary of…").
- **Unresolved author note / TBD**: "not sure", "to be decided", "will be
  finalized", "verify when lab setup available", "TODO", "???", tracked open
  questions.
- **Empty mandatory section**: a required heading with no body content.
- **Empty required-table cell**: a data cell that must carry a value and is
  blank with no explicit "field not available" note.
- **Blank cover field**: Release, Document Revision, Distribution Status, or
  Publication Date missing/unfilled.

## Major  → report, don't fail
- **Missing mandatory section** (per `template-structure.json`). Structural
  deviations are Majors, not Blockers — integrations legitimately differ.
- **Cross-section inconsistency**: intervals (15/30-min), version gates
  ("7.4.x", "8.0 and later"), or the supported media-type list disagree between
  sections.
- **Stale / wrong product name**: a superseded vendor name or inconsistent
  spelling/spacing of the integration name (e.g. an old product name surviving
  a rename, "GenesysCloud" vs "Genesys Cloud CX").

## Minor  → report
- Missing **expected** (not mandatory) section.
- Terminology drift, stale copyright year, typos, unbalanced parentheses,
  broken/truncated sentences.

## Info  → verify, no penalty
- Conditional section absent (fine if N/A).
- Diagram-bearing section: confirm the image is embedded.
- Table with empty cells: confirm none are required data.

## Canonical structure decisions (do not revert)
- **Customer Responsibilities is its own chapter (Chapter 2)**, between
  Introduction and Overview — by decision. Do **not** fold it under Technical
  Solution. `template-structure.json` and `nice-cig-writer` are both aligned to
  this; keep them in sync if either changes.

## Structure placement note
The template lists the "Agent Activity" subsections (Generation Convention,
Summary, Details, Scenario Considerations, Observations) under Chapter 5
(Real-Time). Real guides sometimes place these under Chapter 4 (Historical)
when the activity data is delivered via the historical file. Treat section
*placement* as flexible: if a required section exists *somewhere* in the guide,
it counts as present. Only its total absence is a Major.
