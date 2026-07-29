#!/usr/bin/env python3
"""
scan.py -- Automated publish-gate detectors for a Customer Integration Guide.

Consumes the JSON from extract.py and the canonical template-structure.json,
and emits candidate findings as JSON. This script only catches the
*mechanizable* rules; a reviewer (Claude, guided by SKILL.md + rubric.md) then
curates them and adds judgement-based findings (accuracy, clarity, subtle
consistency) before the gate verdict is issued.

Severity model (see rubric.md):
  blocker : leftover placeholder in prose, leftover template scaffolding,
            unresolved author note / TBD, empty MANDATORY section or empty
            required-table cell, blank cover field.
  major   : missing mandatory section, cross-section inconsistency,
            structural deviation from template.
  minor   : missing 'expected' section, terminology drift, typo-ish.
  info    : diagram-bearing section to verify, conditional section absent.

Usage:  python3 scan.py guide.json template-structure.json  [> findings.json]
"""
import sys, json, re

# ---- patterns -------------------------------------------------------------
PLACEHOLDER = re.compile(r'<([^<>\n]{1,60})>')
# Angle-bracket tokens that are legitimate spec/payload syntax (do NOT flag).
SPEC_TOKEN = re.compile(
    r'(logon\s*id|agent\s*state|start\s*(time|date)|reason\s*code|node\s*id|'
    r'node|rc|id)\b', re.I)

SCAFFOLDING = [
    r'^\s*Example\s*:?\s*$', r'The documentation team will create',
    r'\(This section outlines', r'should be provided if they provide',
    r'\(Architecture\s*\)', r'Mapping of Vendor Attributes to WFM Attributes',
    r'Indicate each', r'Provide specifics on', r'Summary of connectivity',
    r'Summary of convention', r'Does the integration support',
    r'\(see IDD\)', r'from the Historical XML Spec',
    r'Call out what may be important', r'High-level summary of',
    r'This chapter describes the architecture',
]
SCAFFOLDING_RE = re.compile('|'.join(SCAFFOLDING), re.I)

AUTHOR_NOTE = re.compile(
    r'\b(TBD|TODO|FIXME|XXX)\b|not sure|to be decided|will be decided|'
    r'will be final(?:e|ize)|to be finalized|to be verified|needs? to be verified|'
    r'verify when|should be verified when|placeholder|lorem ipsum|'
    r'replace before publishing|fill in|<comment>|\?\?\?|to be confirmed|to be added',
    re.I)

# interval / version / product signals for consistency seeding
INTERVAL = re.compile(r'\b(15|30)[-\s]?minute\b', re.I)
VERSION = re.compile(r'\b(?:WFM\s*)?R?\d\.\d(?:\.\d+)?x?\b')


def matches_section(heading, section):
    h = heading.lower()
    return any(m.lower() in h for m in section["match"])


def section_body_texts(blocks, start_i):
    """Text/blocks that belong to the heading at index start_i, up to the next
    heading of the same or higher level."""
    start = None
    for pos, b in enumerate(blocks):
        if b["i"] == start_i:
            start = pos
            base_level = b.get("level", 9)
            break
    if start is None:
        return []
    out = []
    for b in blocks[start + 1:]:
        lvl = b.get("level")
        if b["type"] == "para" and lvl is not None and lvl <= base_level:
            break
        out.append(b)
    return out


def main():
    guide = json.load(open(sys.argv[1]))
    tpl = json.load(open(sys.argv[2]))
    blocks = guide["blocks"]
    outline = guide["outline"]
    findings = []

    def add(sev, cat, msg, where='', before='', after=''):
        f = {"severity": sev, "category": cat, "message": msg}
        if where:
            f["where"] = where
        if before:
            f["before"] = before
        if after:
            f["after"] = after
        findings.append(f)

    # 1. cover fields -------------------------------------------------------
    for label in tpl["cover_fields"]:
        val = (guide.get("cover") or {}).get(label, '')
        if not val or PLACEHOLDER.search(val):
            add("blocker", "cover", f"Cover field '{label}' is blank or unfilled.",
                where="Cover page")

    # 2. structure coverage -------------------------------------------------
    for section in tpl["sections"]:
        hit = next((o for o in outline if matches_section(o["text"], section)), None)
        if hit:
            continue
        need = section["need"]
        if need == "mandatory":
            add("major", "structure",
                f"Mandatory section not found: '{section['match'][0]}' (template ch.{section['chapter']}). Confirm intentional or add.")
        elif need == "expected":
            add("minor", "structure",
                f"Expected section not found: '{section['match'][0]}'.")
        else:  # conditional
            add("info", "structure",
                f"Conditional section absent (fine if N/A): '{section['match'][0]}'.")

    # 3. per-block content scans -------------------------------------------
    for b in blocks:
        if b["type"] == "table":
            # empty cells in tables (report; reviewer decides if required)
            if b.get("empty_cells"):
                add("info", "table",
                    f"Table (block {b['i']}) has {len(b['empty_cells'])} empty cell(s) — verify none are required data.")
            continue
        text = b.get("text", '')
        if not text:
            continue
        # placeholders in prose (skip spec tokens)
        for m in PLACEHOLDER.finditer(text):
            tok = m.group(1)
            if SPEC_TOKEN.search(tok):
                continue
            add("blocker", "placeholder",
                f"Unresolved placeholder '<{tok}>' left in body text.",
                where=text[:90], before=f"<{tok}>")
        # scaffolding
        if SCAFFOLDING_RE.search(text):
            add("blocker", "scaffolding",
                "Leftover template scaffolding / instructional text.",
                where=text[:120], before=text[:120])
        # author notes
        if AUTHOR_NOTE.search(text):
            add("blocker", "author-note",
                "Unresolved author note / TBD content.",
                where=text[:120], before=text[:120])
        # unbalanced parentheses (broken-sentence heuristic)
        if text.count('(') != text.count(')') and len(text) > 15:
            add("minor", "punctuation",
                "Unbalanced parentheses — possible truncated/broken sentence.",
                where=text[:120], before=text[:120])

    # 4. empty mandatory sections (heading followed by no body) -------------
    mand_headings = {section['match'][0]: section for section in tpl["sections"]
                     if section["need"] in ("mandatory", "expected")}
    for o in outline:
        sec = next((s for s in tpl["sections"] if matches_section(o["text"], s)), None)
        if not sec or sec["need"] not in ("mandatory", "expected"):
            continue
        body = section_body_texts(blocks, o["i"])
        has_content = any(
            (bb["type"] == "table") or (bb.get("images")) or
            (bb["type"] == "para" and bb.get("text") and bb.get("level") is None)
            for bb in body)
        if not has_content:
            sev = "blocker" if sec["need"] == "mandatory" else "minor"
            add(sev, "empty-section",
                f"Section '{o['text']}' appears to have no body content.",
                where=o["text"])
        # diagram sections: confirm an image is present
        if sec.get("expects") == "diagram":
            if not any(bb.get("images") for bb in body):
                add("info", "diagram",
                    f"Section '{o['text']}' expects a diagram — confirm an image is embedded (text extraction cannot see images).",
                    where=o["text"])

    # 5. consistency seeds (reviewer resolves) ------------------------------
    intervals, versions = set(), set()
    for b in blocks:
        t = b.get("text", '') if b["type"] == "para" else ' '.join(
            c for row in b.get("rows", []) for c in row)
        for m in INTERVAL.finditer(t):
            intervals.add(m.group(1))
        for m in VERSION.finditer(t):
            versions.add(m.group(0).strip())
    summary = {
        "intervals_mentioned": sorted(intervals),
        "versions_mentioned": sorted(versions),
    }

    counts = {}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1

    json.dump({"counts": counts, "consistency_seeds": summary,
               "findings": findings},
              sys.stdout, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
