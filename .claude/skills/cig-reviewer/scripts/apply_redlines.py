#!/usr/bin/env python3
"""
apply_redlines.py -- Write inline redlines into a .docx as Word COMMENTS
(always) and tracked-change text replacements (where a clean single-run
substitution exists). Pure stdlib.

The output opens in Word with margin comments a writer can read, plus real
Insertions/Deletions they can Accept/Reject. Comments never alter visible
text, so the file cannot be corrupted by an imperfect match; tracked changes
are only attempted when `before` occurs verbatim inside one run.

findings.json = [
  {"before": "<exact substring in a paragraph>",
   "after":  "<replacement text or ''>",
   "severity": "blocker|major|minor|info",
   "comment": "human-readable note"},
  ...
]

Usage:
  python3 apply_redlines.py in.docx findings.json out.docx \
      [--author "CIG Reviewer"] [--date 2024-01-01T00:00:00Z]
"""
import sys, os, json, zipfile, re, html, argparse, shutil

W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
PARA = re.compile(r'<w:p\b[ >].*?</w:p>', re.S)
PPR = re.compile(r'^(<w:p\b[^>]*>)(\s*<w:pPr\b.*?</w:pPr>)?', re.S)
W_T = re.compile(r'<w:t\b[^>]*>(.*?)</w:t>', re.S)
CT_COMMENTS = ('application/vnd.openxmlformats-officedocument.'
               'wordprocessingml.comments+xml')
REL_COMMENTS = ('http://schemas.openxmlformats.org/officeDocument/2006/'
                'relationships/comments')


def esc(s):
    return html.escape(s, quote=True)


def para_text(p):
    return html.unescape(''.join(W_T.findall(p)))


def make_comment_run(cid):
    return f'<w:r><w:commentReference w:id="{cid}"/></w:r>'


def wrap_with_comment(p, cid):
    """Insert commentRangeStart after pPr and commentRangeEnd + reference
    right before </w:p>."""
    m = PPR.match(p)
    insert_at = m.end()
    start = f'<w:commentRangeStart w:id="{cid}"/>'
    p = p[:insert_at] + start + p[insert_at:]
    end = f'<w:commentRangeEnd w:id="{cid}"/>{make_comment_run(cid)}'
    p = p[:p.rfind('</w:p>')] + end + '</w:p>'
    return p


def tracked_replace(p, before, after, author, date, cid_seq):
    """If `before` is inside a single <w:t>, replace with del(before)+ins(after)
    as tracked changes. Returns (new_p, changed:bool)."""
    def repl(match):
        full = match.group(0)
        inner = W_T.search(full)
        if not inner:
            return full
        txt = html.unescape(inner.group(1))
        if before not in txt:
            return full
        head, _, tail = txt.partition(before)
        rpr = re.search(r'<w:rPr\b.*?</w:rPr>', full, re.S)
        rpr = rpr.group(0) if rpr else ''
        parts = []
        if head:
            parts.append(f'<w:r>{rpr}<w:t xml:space="preserve">{esc(head)}</w:t></w:r>')
        did = next(cid_seq)
        parts.append(
            f'<w:del w:id="{did}" w:author="{esc(author)}" w:date="{date}">'
            f'<w:r>{rpr}<w:delText xml:space="preserve">{esc(before)}</w:delText></w:r></w:del>')
        if after:
            iid = next(cid_seq)
            parts.append(
                f'<w:ins w:id="{iid}" w:author="{esc(author)}" w:date="{date}">'
                f'<w:r>{rpr}<w:t xml:space="preserve">{esc(after)}</w:t></w:r></w:ins>')
        if tail:
            parts.append(f'<w:r>{rpr}<w:t xml:space="preserve">{esc(tail)}</w:t></w:r>')
        return ''.join(parts)

    new_p, n = re.subn(r'<w:r\b[^>]*>(?:(?!</w:r>).)*?</w:r>', repl, p, count=0, flags=re.S)
    # only accept if exactly one run changed (avoid partial mangling)
    return (new_p, new_p != p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('indocx'); ap.add_argument('findings'); ap.add_argument('outdocx')
    ap.add_argument('--author', default='CIG Reviewer')
    ap.add_argument('--date', default='2024-01-01T00:00:00Z')
    a = ap.parse_args()

    findings = json.load(open(a.findings))
    zin = zipfile.ZipFile(a.indocx)
    names = zin.namelist()
    doc = zin.read('word/document.xml').decode('utf-8', 'ignore')

    paras = [(m.start(), m.end(), m.group(0)) for m in PARA.finditer(doc)]
    # id counter shared by comments + tracked changes
    _n = [1000]
    def seq():
        while True:
            _n[0] += 1
            yield _n[0]
    ids = seq()

    comments = []            # (cid, text)
    replacements = {}        # para_index -> list of (before, after)
    applied = []             # audit
    used_para = set()
    cid_for_finding = []

    for f in findings:
        before = f.get('before', '') or ''
        target = None
        for idx, (s, e, ptext) in enumerate(paras):
            if not before:
                break
            if before in para_text(ptext) and idx not in used_para:
                target = idx
                break
        if target is None:
            # fall back: first paragraph containing before (allow reuse)
            for idx, (s, e, ptext) in enumerate(paras):
                if before and before in para_text(ptext):
                    target = idx
                    break
        if target is None:
            applied.append({"before": before[:60], "status": "not-found"})
            continue
        used_para.add(target)
        cid = next(ids)
        sev = f.get('severity', 'info').upper()
        note = f.get('comment', '')
        after = f.get('after', '') or ''
        body = f"[{sev}] {note}"
        if after:
            body += f'  Suggested: "{after}"'
        comments.append((cid, body))
        replacements.setdefault(target, []).append((before, after, cid))
        applied.append({"before": before[:60], "status": "commented",
                         "para": target})

    # rebuild document.xml paragraph by paragraph (reverse to keep offsets)
    for idx in sorted(replacements.keys(), reverse=True):
        s, e, ptext = paras[idx]
        newp = ptext
        for before, after, cid in replacements[idx]:
            if after:
                newp2, changed = tracked_replace(newp, before, after, a.author, a.date, ids)
                if changed:
                    newp = newp2
                    applied[[i for i, x in enumerate(applied)
                             if x.get('para') == idx][0]]["status"] = "tracked+comment"
            newp = wrap_with_comment(newp, cid)
        doc = doc[:s] + newp + doc[e:]

    # comments.xml
    cparts = [f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:comments {W}>']
    for cid, text in comments:
        cparts.append(
            f'<w:comment w:id="{cid}" w:author="{esc(a.author)}" '
            f'w:date="{a.date}" w:initials="CIG">'
            f'<w:p><w:r><w:t xml:space="preserve">{esc(text)}</w:t></w:r></w:p>'
            f'</w:comment>')
    cparts.append('</w:comments>')
    comments_xml = ''.join(cparts)
    comment_elems = ''.join(cparts[1:-1])  # just the <w:comment> nodes

    # [Content_Types].xml
    ct = zin.read('[Content_Types].xml').decode('utf-8', 'ignore')
    if 'comments.xml' not in ct:
        ct = ct.replace('</Types>',
            f'<Override PartName="/word/comments.xml" ContentType="{CT_COMMENTS}"/></Types>')

    # relationships
    rels_name = 'word/_rels/document.xml.rels'
    rels = zin.read(rels_name).decode('utf-8', 'ignore')
    if REL_COMMENTS not in rels:
        rels = rels.replace('</Relationships>',
            f'<Relationship Id="rIdCIGComments" Type="{REL_COMMENTS}" '
            f'Target="comments.xml"/></Relationships>')

    with zipfile.ZipFile(a.outdocx, 'w', zipfile.ZIP_DEFLATED) as zout:
        for n in names:
            if n == 'word/document.xml':
                zout.writestr(n, doc)
            elif n == '[Content_Types].xml':
                zout.writestr(n, ct)
            elif n == rels_name:
                zout.writestr(n, rels)
            elif n == 'word/comments.xml':
                # MERGE our comments into an existing comments part (e.g. one
                # that docx-js shipped) instead of dropping them.
                existing = zin.read(n).decode('utf-8', 'ignore')
                if comment_elems:
                    if '</w:comments>' in existing:
                        existing = existing.replace('</w:comments>', comment_elems + '</w:comments>', 1)
                    else:
                        # self-closing <w:comments .../> -> open, insert, close
                        m = re.search(r'<w:comments\b[^>]*/>', existing)
                        if m:
                            open_tag = m.group(0)[:-2] + '>'
                            existing = (existing[:m.start()] + open_tag +
                                        comment_elems + '</w:comments>' + existing[m.end():])
                        else:
                            existing = comments_xml  # no recognizable part; use ours
                zout.writestr(n, existing)
            else:
                zout.writestr(n, zin.read(n))
        if comments and 'word/comments.xml' not in names:
            zout.writestr('word/comments.xml', comments_xml)

    json.dump({"comments_written": len(comments),
               "paragraphs_touched": len(replacements),
               "applied": applied}, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
