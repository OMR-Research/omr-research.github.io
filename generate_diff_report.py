#!/usr/bin/env python3
"""
generate_diff_report.py — Generate sanity-check.html comparing the current
OMR-Research.bib against a baseline git commit.

Usage:
    python3 generate_diff_report.py                   # compare against default baseline
    python3 generate_diff_report.py <commit>          # compare against any commit

The default baseline (3bb06ea5) is the last manually verified state before
the automated enrichment pass.
"""

import argparse
import re
import sys
import html as html_mod
import subprocess
from pathlib import Path

DEFAULT_BASELINE = "3bb06ea5"

BASE = Path(__file__).parent
OUT = BASE / "diff-report.html"

# ── CLI ─────────────────────────────────────────────────────────────────────


def parse_args():
    p = argparse.ArgumentParser(
        description="Generate sanity-check.html comparing OMR-Research.bib to a baseline commit."
    )
    p.add_argument(
        "baseline",
        nargs="?",
        default=DEFAULT_BASELINE,
        help=f"Git commit to compare against (default: {DEFAULT_BASELINE})",
    )
    return p.parse_args()


# ── Parser (copied from generate_site.py) ────────────────────────────────────


def parse_bib_text(text):
    entries = []
    for m in re.finditer(r"@(\w+)\s*[\{(]", text):
        etype = m.group(1)
        if etype.lower() in ("comment", "string", "preamble"):
            continue
        start = m.start()
        depth = 0
        pos = m.end() - 1
        entry_end = len(text)
        while pos < len(text):
            if text[pos] in "{(":
                depth += 1
            elif text[pos] in "})":
                depth -= 1
                if depth == 0:
                    entry_end = pos + 1
                    break
            pos += 1
        entries.append(_parse_entry(text[start:entry_end], etype))
    return [e for e in entries if e]


def _parse_entry(txt, etype):
    km = re.match(r"@\w+\s*[\{(]\s*([^,\s]+)\s*,", txt)
    if not km:
        return None
    key = km.group(1).strip()
    fields = {"ENTRYTYPE": etype, "ID": key, "_raw": txt}
    pos = km.end()
    while pos < len(txt):
        while pos < len(txt) and txt[pos] in " \t\n\r":
            pos += 1
        if pos >= len(txt) or txt[pos] in "})":
            break
        fm = re.match(r"(\w+)\s*=\s*", txt[pos:])
        if not fm:
            pos += 1
            continue
        fname = fm.group(1).lower()
        pos += fm.end()
        if pos >= len(txt):
            break
        if txt[pos] == "{":
            depth = 0
            vstart = pos + 1
            while pos < len(txt):
                if txt[pos] == "{":
                    depth += 1
                elif txt[pos] == "}":
                    depth -= 1
                    if depth == 0:
                        fval = txt[vstart:pos]
                        pos += 1
                        break
                pos += 1
            else:
                fval = txt[vstart:]
        elif txt[pos] == '"':
            vstart = pos + 1
            pos += 1
            while pos < len(txt) and txt[pos] != '"':
                pos += 1
            fval = txt[vstart:pos]
            pos += 1
        else:
            vstart = pos
            while pos < len(txt) and txt[pos] not in ",})\n":
                pos += 1
            fval = txt[vstart:pos].strip()
        fields[fname] = fval.strip()
        while pos < len(txt) and txt[pos] in " \t\n\r":
            pos += 1
        if pos < len(txt) and txt[pos] == ",":
            pos += 1
    return fields


# ── LaTeX → Unicode (synced with generate_site.py) ───────────────────────────

_ACUTE = dict(zip("aeiouynAEIOUYN", "áéíóúýńÁÉÍÓÚÝŃ"))
_GRAVE = dict(zip("aeiouAEIOU", "àèìòùÀÈÌÒÙ"))
_CIRC = dict(zip("aeiouAEIOU", "âêîôûÂÊÎÔÛ"))
_UML = dict(zip("aeiouAEIOU", "äëïöüÄËÏÖÜ"))
_TILDE = dict(zip("anoANO", "ãñõÃÑÕ"))
_CARON = {
    "c": "č",
    "s": "š",
    "z": "ž",
    "r": "ř",
    "n": "ň",
    "e": "ě",
    "d": "ď",
    "t": "ť",
    "C": "Č",
    "S": "Š",
    "Z": "Ž",
    "R": "Ř",
    "N": "Ň",
    "E": "Ě",
    "D": "Ď",
    "T": "Ť",
}
_CED = {"c": "ç", "C": "Ç", "s": "ş", "S": "Ş"}
_BREVE = {"a": "ă", "A": "Ă", "g": "ğ", "G": "Ğ", "e": "ĕ", "E": "Ĕ"}
_MACRON = {"a": "ā", "A": "Ā", "e": "ē", "E": "Ē", "u": "ū", "U": "Ū"}
_HUNGDBL = {"o": "ő", "O": "Ő", "u": "ű", "U": "Ű"}
_DOT = {"z": "ż", "Z": "Ż", "i": "į", "I": "Į"}
_OGONEK = {"a": "ą", "A": "Ą", "e": "ę", "E": "Ę"}
_AMAP = {
    "'": _ACUTE,
    "`": _GRAVE,
    "^": _CIRC,
    '"': _UML,
    "~": _TILDE,
    "v": _CARON,
    "c": _CED,
    "u": _BREVE,
    "=": _MACRON,
    "H": _HUNGDBL,
    ".": _DOT,
    "k": _OGONEK,
}


def _sa(cmd, ch):
    return _AMAP.get(cmd, {}).get(ch, ch)


def l2u(s):
    if not s:
        return s
    s = re.sub(r"\\\\(\\[%&#_])", r"\1", s)
    s = re.sub(r"\{\\'\{?\\i\}?\}", "í", s)
    s = re.sub(r"\{\\`\{?\\i\}?\}", "ì", s)
    CMDS = r"'`\^\"~vcuH=\.k"
    s = re.sub(
        r"\{\\([" + CMDS + r"])\{([a-zA-Z])\}\}",
        lambda m: _sa(m.group(1), m.group(2)),
        s,
    )
    s = re.sub(
        r"\\([" + CMDS + r"])\{([a-zA-Z])\}", lambda m: _sa(m.group(1), m.group(2)), s
    )
    s = re.sub(
        r"\{\\([" + CMDS + r"])([a-zA-Z])\}", lambda m: _sa(m.group(1), m.group(2)), s
    )
    s = re.sub(
        r"\\([" + CMDS + r"])([a-zA-Z])", lambda m: _sa(m.group(1), m.group(2)), s
    )
    for p, r in [
        (r"\{?\\ss\}?", "ß"),
        (r"\{?\\l\}?", "ł"),
        (r"\{?\\L\}?", "Ł"),
        (r"\{?\\o\}?", "ø"),
        (r"\{?\\O\}?", "Ø"),
        (r"\{?\\ae\}?", "æ"),
        (r"\{?\\AE\}?", "Æ"),
        (r"\{?\\oe\}?", "œ"),
        (r"\{?\\OE\}?", "Œ"),
        (r"\\&", "&"),
        (r"\\%", "%"),
        (r"\\_", "_"),
        (r"\\#", "#"),
        (r"\\textendash\b", "–"),
        (r"\\textemdash\b", "—"),
        (r"\\ldots\b", "…"),
        (r"\\url\{[^}]*\}", ""),
        (r"\\href\{[^}]*\}\{([^}]*)\}", r"\1"),
    ]:
        s = re.sub(p, r, s)
    for _ in range(6):
        prev = s
        s = re.sub(r"\{([^{}]*)\}", r"\1", s)
        if s == prev:
            break
    s = s.replace("---", "—").replace("--", "–")
    s = re.sub(r"~", " ", s)
    s = re.sub(r"[\s·]+$", "", s)
    return s.strip()


# ── Source link helper ───────────────────────────────────────────────────────


def source_link(e):
    file_val = e.get("file", "")
    m = re.match(r":([^:]+):PDF", file_val, re.IGNORECASE)
    if not m:
        m = re.match(r"([^:]+):PDF", file_val, re.IGNORECASE)
    if m:
        rel = m.group(1).strip()
        return ("PDF", f"./{rel}")
    url = e.get("url", "").strip()
    if url:
        return ("URL", url)
    doi = e.get("doi", "").strip()
    if doi:
        return ("DOI", f"https://doi.org/{doi}")
    arxiv = e.get("eprint", "").strip()
    if arxiv:
        return ("arXiv", f"https://arxiv.org/abs/{arxiv}")
    return None


# ── Compare entries ──────────────────────────────────────────────────────────

IGNORE_FIELDS = {"_raw"}
DOI_URL_FIELDS = {"doi", "url", "eprint"}


def compare(base_map, curr_map):
    new_entries = []
    abstract_added = []
    pdf_changed = []
    link_changed = []
    meta_changed = []

    for key, ce in curr_map.items():
        if key not in base_map:
            new_entries.append(ce)
            continue
        be = base_map[key]
        abs_diff = doi_diff = pdf_diff = meta_diff = False
        abs_row = doi_rows = pdf_rows = None

        all_fields = set(be) | set(ce) - IGNORE_FIELDS - {"ENTRYTYPE", "ID"}
        for f in sorted(all_fields):
            if f in IGNORE_FIELDS or f in ("entrytype", "id"):
                continue
            bv = be.get(f, "").strip()
            cv = ce.get(f, "").strip()
            if bv == cv:
                continue
            if f == "abstract":
                abs_diff = True
                abs_row = (bv, cv)
            elif f == "file":
                pdf_diff = True
                pdf_rows = (bv, cv)
            elif f in DOI_URL_FIELDS:
                doi_diff = True
                doi_rows = (f, bv, cv)
            else:
                meta_diff = True

        if abs_diff:
            abstract_added.append((ce, abs_row))
        if pdf_diff:
            pdf_changed.append((ce, pdf_rows))
        if doi_diff:
            link_changed.append((ce, doi_rows))
        if meta_diff and not abs_diff and not pdf_diff and not doi_diff:
            meta_changed.append(ce)

    return new_entries, abstract_added, pdf_changed, link_changed, meta_changed


# ── HTML rendering ───────────────────────────────────────────────────────────


def H(s):
    return html_mod.escape(str(s))


def badge(e):
    return f'<span class="badge new-badge">{H(e.get("ENTRYTYPE", "?"))}</span>'


def year_span(e):
    y = e.get("year", "")
    return f'<span class="year">{H(y)}</span>' if y else ""


def src_chip(e):
    lnk = source_link(e)
    if not lnk:
        return ""
    label, href = lnk
    return f' <a class="src-link" href="{H(href)}" target="_blank">↗ {label}</a>'


def entry_head(e):
    key = e.get("ID", "?")
    title = l2u(e.get("title", ""))
    return f"""
      <div class="entry-head">
        <span class="key">{H(key)}</span>{badge(e)}{year_span(e)}{src_chip(e)}
      </div>
      <div class="title">{H(title)}</div>"""


def rows_from_entry(e, show_abstract=True):
    out = ""
    auth = l2u(e.get("author", ""))
    if auth:
        out += f'<tr><td class="field">author</td><td colspan="2">{H(auth)}</td></tr>\n'
    if show_abstract:
        ab = l2u(e.get("abstract", ""))
        if ab:
            out += f'<tr><td class="field">abstract</td><td colspan="2" class="abs">{H(ab)}</td></tr>\n'
    return out


def render_new(entries):
    out = ""
    for e in entries:
        out += '<div class="entry">' + entry_head(e)
        out += (
            '<table class="diff-table"><tbody>'
            + rows_from_entry(e)
            + "</tbody></table></div>"
        )
    return out


def render_abstract_added(entries):
    out = ""
    for e, (bv, cv) in entries:
        bv_d, cv_d = l2u(bv), l2u(cv)
        out += '<div class="entry">' + entry_head(e)
        out += '<table class="diff-table"><tbody>'
        out += f'<tr class="{"changed" if bv else ""}"><td class="field">abstract</td>'
        out += f'<td class="old abs">{H(bv_d) if bv_d else "<em>—</em>"}</td>'
        out += f'<td class="new abs">{H(cv_d) if cv_d else "<em>—</em>"}</td></tr>'
        out += "</tbody></table></div>"
    return out


def render_pdf_changed(entries):
    out = ""
    for e, (bv, cv) in entries:
        out += '<div class="entry">' + entry_head(e)
        out += '<table class="diff-table"><tbody>'
        out += '<tr class="changed"><td class="field">file</td>'
        out += f'<td class="old">{H(bv) if bv else "<em>—</em>"}</td>'
        out += f'<td class="new">{H(cv) if cv else "<em>—</em>"}</td></tr>'
        out += "</tbody></table></div>"
    return out


def render_link_changed(entries):
    out = ""
    for e, (field, bv, cv) in entries:
        out += '<div class="entry">' + entry_head(e)
        out += '<table class="diff-table"><tbody>'
        out += f'<tr class="changed"><td class="field">{H(field)}</td>'
        out += f'<td class="old">{H(bv) if bv else "<em>—</em>"}</td>'
        out += f'<td class="new">{H(cv) if cv else "<em>—</em>"}</td></tr>'
        out += "</tbody></table></div>"
    return out


def render_meta(entries):
    out = ""
    for e in entries:
        out += '<div class="entry">' + entry_head(e)
        out += '<table class="diff-table"><tbody>'
        out += rows_from_entry(e, show_abstract=False)
        out += "</tbody></table></div>"
    return out


def section(id_, title, color, count, body):
    if not count:
        return ""
    return f"""
<section id="{id_}">
  <h2 style="background:{color};color:#fff">{title} ({count})</h2>
  {body}
</section>"""


# ── Main ─────────────────────────────────────────────────────────────────────


def main():
    args = parse_args()
    baseline = args.baseline

    result = subprocess.run(
        ["git", "show", f"{baseline}:OMR-Research.bib"],
        capture_output=True,
        text=True,
        cwd=BASE,
    )
    if result.returncode != 0:
        print(
            f"ERROR: could not read OMR-Research.bib from commit {baseline!r}",
            file=sys.stderr,
        )
        print(result.stderr, file=sys.stderr)
        sys.exit(1)

    base_entries = parse_bib_text(result.stdout)
    curr_entries = parse_bib_text(
        (BASE / "OMR-Research.bib").read_text(encoding="utf-8")
    )

    base_map = {e["ID"]: e for e in base_entries}
    curr_map = {e["ID"]: e for e in curr_entries}

    new_entries, abstract_added, pdf_changed, link_changed, meta_changed = compare(
        base_map, curr_map
    )

    total_changed = (
        len(abstract_added) + len(pdf_changed) + len(link_changed) + len(meta_changed)
    )

    toc_items = []
    if new_entries:
        toc_items.append(
            f'<li><a href="#sec-new">New entries: {len(new_entries)}</a></li>'
        )
    if abstract_added:
        toc_items.append(
            f'<li><a href="#sec-abstract">Abstract added/changed: {len(abstract_added)}</a></li>'
        )
    if pdf_changed:
        toc_items.append(
            f'<li><a href="#sec-pdf">PDF link added/changed: {len(pdf_changed)}</a></li>'
        )
    if link_changed:
        toc_items.append(
            f'<li><a href="#sec-doi">DOI/URL changed: {len(link_changed)}</a></li>'
        )
    if meta_changed:
        toc_items.append(
            f'<li><a href="#sec-meta">Other metadata: {len(meta_changed)}</a></li>'
        )

    body = section(
        "sec-new", "NEW ENTRIES", "#1a7a4a", len(new_entries), render_new(new_entries)
    )
    body += section(
        "sec-abstract",
        "ABSTRACT ADDED/CHANGED",
        "#155799",
        len(abstract_added),
        render_abstract_added(abstract_added),
    )
    body += section(
        "sec-pdf",
        "PDF LINK ADDED/CHANGED",
        "#6c757d",
        len(pdf_changed),
        render_pdf_changed(pdf_changed),
    )
    body += section(
        "sec-doi",
        "DOI/URL CHANGED",
        "#6c4000",
        len(link_changed),
        render_link_changed(link_changed),
    )
    body += section(
        "sec-meta",
        "OTHER METADATA CHANGED",
        "#555",
        len(meta_changed),
        render_meta(meta_changed),
    )

    short = baseline[:8]
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>OMR-Research.bib — Changes since {short}</title>
<style>
@import url('https://fonts.googleapis.com/css?family=Open+Sans');
body{{font-family:"Open Sans",Arial,sans-serif;margin:0;background:#f8f9fa;color:#212529;font-size:14px}}
.header{{background:linear-gradient(120deg,#155799,#159957);color:#fff;padding:30px 24px 20px}}
.header h1{{margin:0 0 6px;font-size:28px}} .header p{{margin:0;opacity:.85}}
.toc{{background:#fff;border-bottom:1px solid #dee2e6;padding:14px 24px}}
.toc h2{{margin:0 0 8px;font-size:15px}} .toc ul{{margin:0;padding-left:20px;columns:3;-webkit-columns:3}}
.toc a{{color:#155799}}
main{{max-width:1200px;margin:0 auto;padding:16px 24px}}
section{{margin-bottom:28px}}
h2{{font-size:15px;padding:8px 14px;border-radius:4px 4px 0 0;margin:0}}
.entry{{background:#fff;border:1px solid #dee2e6;border-top:none;padding:12px 14px 10px}}
.entry+.entry{{border-top:none}}
.entry-head{{display:flex;flex-wrap:wrap;align-items:baseline;gap:8px;margin-bottom:4px}}
.key{{font-family:monospace;font-weight:700;font-size:13px;color:#155799}}
.badge{{font-size:11px;padding:1px 7px;border-radius:3px;font-weight:600}}
.new-badge{{background:#1a7a4a;color:#fff}}
.year{{font-size:12px;color:#888}}
.title{{font-size:13px;color:#444;font-style:italic;margin-bottom:8px}}
.src-link{{font-size:11px;padding:2px 8px;border-radius:3px;background:#e8f0fe;color:#155799;
           text-decoration:none;border:1px solid #b8d0f8;margin-left:auto;white-space:nowrap}}
.src-link:hover{{background:#d0e4ff}}
.diff-table{{width:100%;border-collapse:collapse;font-size:13px}}
.diff-table th{{text-align:left;background:#f0f0f0;padding:4px 8px;font-weight:600;font-size:12px}}
.diff-table td{{padding:4px 8px;vertical-align:top;border-top:1px solid #f0f0f0}}
.field{{font-family:monospace;font-size:12px;color:#888;white-space:nowrap;width:90px}}
.old{{color:#842029;background:#fff8f8;width:45%}}
.new{{color:#0f5132;background:#f6fff9;width:45%}}
.abs{{font-size:12px;line-height:1.5}}
.removed .old{{background:#f8d7da}}
.changed .old{{background:#fff3cd}}
</style></head>
<body>
<div class="header">
  <h1>OMR-Research.bib — Diff Report</h1>
  <p>All changes since baseline commit <code>{baseline}</code> &nbsp;·&nbsp;
     {len(new_entries)} new entries &nbsp;·&nbsp; {total_changed} changed entries</p>
</div>
<div class="toc"><h2>Jump to section</h2><ul>{"".join(toc_items)}</ul></div>
<main>{body}</main>
</body></html>"""

    OUT.write_text(html, encoding="utf-8")
    print(f"Written {OUT}")
    print(
        f"  New: {len(new_entries)}, Abstract: {len(abstract_added)}, PDF: {len(pdf_changed)}, DOI/URL: {len(link_changed)}, Meta: {len(meta_changed)}"
    )


if __name__ == "__main__":
    main()
