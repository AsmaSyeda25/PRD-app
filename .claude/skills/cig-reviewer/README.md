# cig-reviewer

A publish-gate reviewer for NiCE WFM **Customer Integration Guides** (CIGs).
Point it at a guide `.docx` and it returns a **READY / NOT READY** verdict plus
a redlined `.docx`.

Invoke it in Claude Code with `/cig-reviewer` (or just ask to "review /
gate this integration guide"). The orchestration lives in [`SKILL.md`](SKILL.md).

## What it checks
Structure, format/hygiene, and internal consistency — **not** external technical
accuracy (mappings vs. IDD/vendor docs), which is a planned add-on.

- Required chapters/sections present (per the CIG template)
- Cover + revision history filled
- No leftover `<placeholders>`, `Example:` scaffolding, or author notes ("TBD",
  "not sure", "verify when lab setup available")
- Tables intact; no empty required cells
- Intervals (15/30-min), version gates, media-type lists, and the product name
  are consistent across sections

`READY` only when there are **zero blockers**. Majors/minors are the writer's
punch-list.

## Output
- `<guide>_GATE_REVIEW.md` — verdict + prioritized findings with Before → After
- `<guide>_redlined.docx` — Word **comments** on every finding, plus
  **Accept/Reject tracked changes** for clean text replacements

## Files
| Path | Purpose |
|---|---|
| `SKILL.md` | The review workflow the agent follows |
| `reference/template-structure.json` | Canonical CIG structure (mandatory / expected / conditional sections) |
| `reference/rubric.md` | Blocker / Major / Minor / Info severity rules |
| `scripts/extract.py` | `.docx` → structured JSON (outline, blocks, tables, cover) |
| `scripts/scan.py` | Automated detectors → candidate findings JSON |
| `scripts/apply_redlines.py` | Writes comments + tracked changes into the `.docx` |

Scripts are pure-stdlib Python 3 (no external dependencies).

## Quick start
```bash
cd .claude/skills/cig-reviewer
python3 scripts/extract.py "MyGuide.docx" > /tmp/g.json
python3 scripts/scan.py /tmp/g.json reference/template-structure.json > /tmp/f.json
# then curate findings per rubric.md and apply redlines:
python3 scripts/apply_redlines.py "MyGuide.docx" /tmp/redlines.json "MyGuide_redlined.docx"
```

## Scope notes
- Text extraction can't see embedded images; diagram sections are routed to a
  "needs human/image check" list, never flagged as empty.
- PDFs can be reviewed for content (via `pdftotext -layout`) but redlines
  require the `.docx`.
