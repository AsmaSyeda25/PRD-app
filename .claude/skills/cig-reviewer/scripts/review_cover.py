#!/usr/bin/env python3
"""
review_cover.py -- Prepend a gate "review cover sheet" (verdict banner +
findings/blockers table) as page 1 of a reviewed .docx. Pure stdlib.

Turns any reviewed guide into a self-contained *review copy* whose first page
shows the verdict at a glance. Run it on the redlined .docx (from
apply_redlines.py) so the review copy carries both the cover sheet and the
margin comments.

spec.json:
{
  "verdict": "NOT READY",              // or "READY"
  "blockers": 9, "majors": 1, "minors": 4,
  "note": "one-paragraph reviewer note (optional)",
  "table_title": "Blockers - must clear before publish",   // optional
  "columns": ["#", "Section", "What to supply"],           // optional (<=4)
  "rows": [["1","Overview -> Media Channels","..."], ...]   // optional
}

Usage: python3 review_cover.py in.docx spec.json out.docx
"""
import sys, json, zipfile, html, re

def esc(s):
    return html.escape(str(s), quote=True)

def p_shaded(text, fill, color, sz, bold=True, after=40):
    b = '<w:b/>' if bold else ''
    return (f'<w:p><w:pPr><w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>'
            f'<w:spacing w:before="0" w:after="{after}"/></w:pPr>'
            f'<w:r><w:rPr>{b}<w:color w:val="{color}"/><w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/></w:rPr>'
            f'<w:t xml:space="preserve">{esc(text)}</w:t></w:r></w:p>')

def p_text(text, color='000000', sz=22, bold=False, italic=False, after=80):
    b = '<w:b/>' if bold else ''
    i = '<w:i/>' if italic else ''
    return (f'<w:p><w:pPr><w:spacing w:after="{after}"/></w:pPr>'
            f'<w:r><w:rPr>{b}{i}<w:color w:val="{color}"/><w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/></w:rPr>'
            f'<w:t xml:space="preserve">{esc(text)}</w:t></w:r></w:p>')

def note_box(text):
    return (f'<w:p><w:pPr><w:shd w:val="clear" w:color="auto" w:fill="E7F1FB"/>'
            f'<w:pBdr>'
            f'<w:top w:val="single" w:sz="4" w:color="5B9BD5"/>'
            f'<w:bottom w:val="single" w:sz="4" w:color="5B9BD5"/>'
            f'<w:left w:val="single" w:sz="4" w:color="5B9BD5"/>'
            f'<w:right w:val="single" w:sz="4" w:color="5B9BD5"/></w:pBdr>'
            f'<w:spacing w:before="60" w:after="120"/></w:pPr>'
            f'<w:r><w:rPr><w:color w:val="1F4E79"/><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr>'
            f'<w:t xml:space="preserve">{esc(text)}</w:t></w:r></w:p>')

def cell(text, w, header=False):
    shd = '<w:shd w:val="clear" w:color="auto" w:fill="D9E2F3"/>' if header else ''
    b = '<w:b/>' if header else ''
    return (f'<w:tc><w:tcPr><w:tcW w:type="dxa" w:w="{w}"/>{shd}</w:tcPr>'
            f'<w:p><w:pPr><w:spacing w:after="0"/></w:pPr>'
            f'<w:r><w:rPr>{b}<w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr>'
            f'<w:t xml:space="preserve">{esc(text)}</w:t></w:r></w:p></w:tc>')

def table(cols, rows):
    total = 9360
    ncol = max(len(cols), max((len(r) for r in rows), default=0))
    if ncol <= 1:
        widths = [total]
    elif ncol == 3:
        widths = [600, 3600, 5160]
    else:
        w = total // ncol
        widths = [w] * (ncol - 1) + [total - w * (ncol - 1)]
    edge = '<w:tblBorders>' + ''.join(
        f'<w:{s} w:val="single" w:sz="4" w:color="999999"/>'
        for s in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV')) + '</w:tblBorders>'
    grid = '<w:tblGrid>' + ''.join(f'<w:gridCol w:w="{w}"/>' for w in widths) + '</w:tblGrid>'
    trs = []
    trs.append('<w:tr>' + ''.join(cell(c, widths[i], True) for i, c in enumerate(cols)) + '</w:tr>')
    for r in rows:
        cells = [cell(r[i] if i < len(r) else '', widths[i]) for i in range(ncol)]
        trs.append('<w:tr>' + ''.join(cells) + '</w:tr>')
    return (f'<w:tbl><w:tblPr><w:tblW w:type="dxa" w:w="{total}"/>{edge}</w:tblPr>'
            f'{grid}{"".join(trs)}</w:tbl>')

def page_break():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'

def build_cover(spec):
    verdict = str(spec.get('verdict', '')).upper()
    ready = verdict.replace(' ', '') in ('READY',) and 'NOT' not in verdict
    fill = '1E7E34' if ready else 'B00020'
    icon = '✅' if ready else '\U0001F534'
    b, m, mi = spec.get('blockers', 0), spec.get('majors', 0), spec.get('minors', 0)
    parts = [p_shaded(f'{icon}  GATE VERDICT — {verdict}', fill, 'FFFFFF', 36)]
    def plur(n, w):
        return f'{n} {w}' + ('' if n == 1 else 's')
    counts = ' · '.join([plur(b, 'blocker'), plur(m, 'major'), plur(mi, 'minor')])
    parts.append(p_text(counts, color=fill, sz=26, bold=True, after=120))
    if spec.get('note'):
        parts.append(note_box(spec['note']))
    rows = spec.get('rows') or []
    if rows:
        parts.append(p_text(spec.get('table_title', 'Findings'), color='0A3D62', sz=28, bold=True, after=60))
        parts.append(table(spec.get('columns', ['#', 'Finding']), rows))
    parts.append(page_break())
    return ''.join(parts)

def main():
    indocx, specpath, outdocx = sys.argv[1], sys.argv[2], sys.argv[3]
    spec = json.load(open(specpath))
    zin = zipfile.ZipFile(indocx)
    doc = zin.read('word/document.xml').decode('utf-8', 'ignore')
    cover = build_cover(spec)
    # insert right after the <w:body ...> opening tag
    m = re.search(r'<w:body\b[^>]*>', doc)
    if not m:
        sys.exit('no <w:body> found')
    doc = doc[:m.end()] + cover + doc[m.end():]
    with zipfile.ZipFile(outdocx, 'w', zipfile.ZIP_DEFLATED) as zout:
        for n in zin.namelist():
            zout.writestr(n, doc if n == 'word/document.xml' else zin.read(n))
    print(f'wrote {outdocx} (verdict={spec.get("verdict")}, rows={len(spec.get("rows") or [])})')

if __name__ == '__main__':
    main()
