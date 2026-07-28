#!/usr/bin/env python3
"""
extract.py -- Structure/text/table/image extractor for a Customer Integration
Guide .docx (Word). Pure stdlib (zipfile + regex); no external dependencies,
so it runs anywhere python3 is available.

Emits a JSON document describing the guide in reading order:

  {
    "source": "<path>",
    "blocks": [
       {"i": 0, "type": "para",  "style": "Heading1", "level": 1,
        "text": "...", "images": 0, "empty": false},
       {"i": 1, "type": "table", "rows": [[ "cell", ...], ...],
        "empty_cells": [[r,c], ...], "n_rows": 3, "n_cols": 3},
       {"i": 2, "type": "image", "style": "Normal"}
    ],
    "outline": [{"i":0,"level":1,"text":"Introduction"}, ...],
    "cover": {"Release": "...", "Document Revision": "...", ...}
  }

Usage:  python3 extract.py path/to/guide.docx  [> out.json]
"""
import sys, json, zipfile, re, html

W_T   = re.compile(r'<w:t\b[^>]*>(.*?)</w:t>', re.S)
STYLE = re.compile(r'<w:pStyle\s+w:val="([^"]+)"')
PARA  = re.compile(r'<w:p\b[ >].*?</w:p>', re.S)
TBL   = re.compile(r'<w:tbl\b[ >].*?</w:tbl>', re.S)
TC    = re.compile(r'<w:tc\b[ >].*?</w:tc>', re.S)
TR    = re.compile(r'<w:tr\b[ >].*?</w:tr>', re.S)
HAS_IMG = re.compile(r'<w:drawing\b|<pic:pic\b|<v:imagedata\b|<w:object\b')

COVER_LABELS = ["Release", "Document Revision", "Distribution Status",
                "Publication Date"]


def text_of(xml_fragment):
    return html.unescape(''.join(W_T.findall(xml_fragment))).strip()


def style_level(style):
    m = re.match(r'Heading(\d)', style or '')
    if m:
        return int(m.group(1))
    if style in ('Title', 'CoverTitle'):
        return 0
    return None


def parse_table(tbl_xml):
    rows = []
    empty_cells = []
    for r, tr in enumerate(TR.findall(tbl_xml)):
        cells = []
        for c, tc in enumerate(TC.findall(tr)):
            t = text_of(tc)
            cells.append(t)
            if t == '':
                empty_cells.append([r, c])
        rows.append(cells)
    n_cols = max((len(r) for r in rows), default=0)
    return {
        "type": "table",
        "rows": rows,
        "n_rows": len(rows),
        "n_cols": n_cols,
        "empty_cells": empty_cells,
    }


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: extract.py guide.docx")
    path = sys.argv[1]
    z = zipfile.ZipFile(path)
    xml = z.read('word/document.xml').decode('utf-8', 'ignore')
    body = re.search(r'<w:body\b.*</w:body>', xml, re.S)
    if body:
        xml = body.group(0)

    # Collect table spans first so we can skip paragraphs that live inside them.
    tbl_spans = [(m.start(), m.end(), m.group(0)) for m in TBL.finditer(xml)]

    def in_table(pos):
        return any(s <= pos < e for s, e, _ in tbl_spans)

    events = []  # (start, kind, payload)
    for s, e, frag in tbl_spans:
        events.append((s, 'table', frag))
    for m in PARA.finditer(xml):
        if in_table(m.start()):
            continue
        events.append((m.start(), 'para', m.group(0)))
    events.sort(key=lambda x: x[0])

    blocks, outline, cover = [], [], {}
    i = 0
    for _, kind, frag in events:
        if kind == 'table':
            tb = parse_table(frag)
            tb["i"] = i
            blocks.append(tb)
            i += 1
            continue
        style = (STYLE.search(frag) or [None])
        style = STYLE.search(frag)
        style = style.group(1) if style else 'Normal'
        text = text_of(frag)
        images = len(HAS_IMG.findall(frag))
        lvl = style_level(style)
        block = {"i": i, "type": "para", "style": style, "text": text,
                 "images": images, "empty": (text == '' and images == 0)}
        if lvl is not None:
            block["level"] = lvl
        if images and not text:
            block["type"] = "image"
        blocks.append(block)
        if lvl is not None and lvl >= 1 and text:
            outline.append({"i": i, "level": lvl, "text": text})
        i += 1

    # Cover fields: labels appear as their own paragraphs/cells; value is the
    # adjacent non-empty text. Scan flattened text sequence for "Label:" then value.
    flat = []
    for b in blocks:
        if b["type"] == "table":
            for row in b["rows"]:
                flat.extend([c for c in row])
        else:
            flat.append(b.get("text", ""))
    flat = [t for t in flat if t is not None]
    for idx, t in enumerate(flat):
        for label in COVER_LABELS:
            if t.rstrip(':').strip() == label or t.strip() == label + ':':
                val = ''
                for j in range(idx + 1, min(idx + 3, len(flat))):
                    if flat[j].strip():
                        val = flat[j].strip()
                        break
                cover.setdefault(label, val)
            elif t.strip().startswith(label) and ':' in t:
                val = t.split(':', 1)[1].strip()
                if val:
                    cover.setdefault(label, val)

    out = {"source": path, "n_blocks": len(blocks),
           "blocks": blocks, "outline": outline, "cover": cover}
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
