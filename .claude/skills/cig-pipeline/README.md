# cig-pipeline

End-to-end orchestrator for NiCE WFM **Customer Integration Guides**:
**draft → gate-review → revise loop → human approval.** It chains two existing
skills and stops at a human's desk — it never publishes on its own.

```
prompt ─▶ Gate 1: nice-cig-writer (draft .docx, status=Draft)
             │
             ▼
        Gate 2: cig-reviewer  ─▶ verdict + scorecard + redlined .docx
             │
      PASS? (0 blockers & 0 majors)
        ├── no ─▶ mechanical revise (nice-cig-writer) ─┐  up to 3 rounds
        │◀───────────────────────────────────────────┘
        ▼
        Gate 3: Human — final review + the only "Published" flip
```

## Two entry points
- **Create:** "create/draft a CIG for `<vendor>`" (+ notes / Jira / design docs) → starts at Gate 1.
- **Approve:** "review / approve this CIG" (+ an existing draft `.docx`) → skips to Gate 2.

## Locked policy
| Setting | Value |
|---|---|
| Exit bar (loop → human) | **0 blockers AND 0 majors**; minors become the human punch-list |
| Max auto-revise rounds | **3**, then ESCALATE to human with remaining findings |
| Auto-fix scope | **mechanical only** (hygiene/format/typos/consistency); content & accuracy gaps become questions for the human — never fabricated |
| Publishing | **Human only.** Pipeline keeps status = Draft throughout |

## Depends on
- [`nice-cig-writer`](../../../../.claude/skills/nice-cig-writer) — draft/revise (Gate 1)
- [`cig-reviewer`](../cig-reviewer) — publish gate + scorecard (Gate 2)

## Files
| Path | Purpose |
|---|---|
| `SKILL.md` | The conductor runbook (gates, loop, decision package) |
| `scripts/run_state.py` | Audit log of every round + the PASS/CONTINUE/ESCALATE decision + loop cap |

`run_state.py` is pure-stdlib Python 3.

## Quick start
```bash
cd .claude/skills/cig-pipeline
python3 scripts/run_state.py init /tmp/run.json --guide "Genesys.docx" --mode create --max-rounds 3
# ...conductor runs Gate 1/2, recording each round:
python3 scripts/run_state.py record /tmp/run.json --round 1 --verdict NOT_READY --blockers 3 --majors 2 --minors 5
python3 scripts/run_state.py show /tmp/run.json
```
