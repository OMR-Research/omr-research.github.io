#!/usr/bin/env python3
"""
generate_site.py — replaces the bibtex2html + RenderWebsite.sh pipeline.

Generates interactive, self-contained HTML pages from the OMR Research bib files.
Includes BibTeX sanity checks equivalent to bibtex2html warnings.

Usage:
    python3 generate_site.py          # generate all pages
    python3 generate_site.py --check  # sanity-check only, no output
"""

import re
import sys
import json
import html as html_mod
from datetime import date
from pathlib import Path

BASE = Path(__file__).parent
TODAY = date.today().strftime("%d.%m.%Y")

# ─── BibTeX Parser ──────────────────────────────────────────────────────────


def parse_bib(path):
    """Parse a .bib file; return list of entry dicts with all fields lowercase."""
    text = Path(path).read_text(encoding="utf-8")
    entries = []

    # Locate each entry by @Type{ or @Type(
    for m in re.finditer(r"@(\w+)\s*[\{(]", text):
        etype = m.group(1)
        if etype.lower() in ("comment", "string", "preamble"):
            continue

        # Walk brace-balanced content from this @
        start = m.start()
        depth = 0
        pos = m.end() - 1  # position of opening brace
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

        entry_text = text[start:entry_end]
        entry = _parse_entry_fields(entry_text, etype)
        if entry:
            entries.append(entry)

    return entries


def _parse_entry_fields(entry_text, etype):
    """Parse fields from a single BibTeX entry block."""
    # Extract key: @Type{key,
    km = re.match(r"@\w+\s*[\{(]\s*([^,\s]+)\s*,", entry_text)
    if not km:
        return None
    key = km.group(1).strip()
    fields = {"ENTRYTYPE": etype, "ID": key, "_raw": entry_text}

    pos = km.end()
    text = entry_text

    while pos < len(text):
        # Skip whitespace
        while pos < len(text) and text[pos] in " \t\n\r":
            pos += 1
        if pos >= len(text) or text[pos] in "})":
            break

        # Field name
        fm = re.match(r"(\w+)\s*=\s*", text[pos:])
        if not fm:
            pos += 1
            continue
        fname = fm.group(1).lower()
        pos += fm.end()

        if pos >= len(text):
            break

        # Field value
        if text[pos] == "{":
            depth = 0
            vstart = pos + 1
            while pos < len(text):
                if text[pos] == "{":
                    depth += 1
                elif text[pos] == "}":
                    depth -= 1
                    if depth == 0:
                        fval = text[vstart:pos]
                        pos += 1
                        break
                pos += 1
            else:
                fval = text[vstart:]
        elif text[pos] == '"':
            vstart = pos + 1
            pos += 1
            while pos < len(text) and text[pos] != '"':
                pos += 1
            fval = text[vstart:pos]
            pos += 1
        else:
            vstart = pos
            while pos < len(text) and text[pos] not in ",})\n":
                pos += 1
            fval = text[vstart:pos].strip()

        fields[fname] = fval.strip()

        # Skip comma
        while pos < len(text) and text[pos] in " \t\n\r":
            pos += 1
        if pos < len(text) and text[pos] == ",":
            pos += 1

    return fields


# ─── LaTeX → Unicode ────────────────────────────────────────────────────────

_ACUTE = dict(zip("aeiouynAEIOUYN", "áéíóúýńÁÉÍÓÚÝŃ"))
_GRAVE = dict(zip("aeiouAEIOU", "àèìòùÀÈÌÒÙ"))
_CIRC = dict(zip("aeiouAEIOU", "âêîôûÂÊÎÔÛ"))
_UMLAUT = dict(zip("aeiouAEIOU", "äëïöüÄËÏÖÜ"))
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
_CEDILLA = {"c": "ç", "C": "Ç", "s": "ş", "S": "Ş"}
_BREVE = {"a": "ă", "A": "Ă", "g": "ğ", "G": "Ğ", "e": "ĕ", "E": "Ĕ"}
_MACRON = {"a": "ā", "A": "Ā", "e": "ē", "E": "Ē", "u": "ū", "U": "Ū"}
_HUNGDBL = {"o": "ő", "O": "Ő", "u": "ű", "U": "Ű"}
_DOT = {"z": "ż", "Z": "Ż", "i": "į", "I": "Į"}
_OGONEK = {"a": "ą", "A": "Ą", "e": "ę", "E": "Ę"}
_STROKE = {"l": "ł", "L": "Ł", "o": "ø", "O": "Ø"}

_ACCENT_MAP = {
    "'": _ACUTE,
    "`": _GRAVE,
    "^": _CIRC,
    '"': _UMLAUT,
    "~": _TILDE,
    "v": _CARON,
    "c": _CEDILLA,
    "u": _BREVE,
    "=": _MACRON,
    "H": _HUNGDBL,
    ".": _DOT,
    "k": _OGONEK,
}


def _sub_accent(cmd, ch):
    table = _ACCENT_MAP.get(cmd, {})
    return table.get(ch, ch)


def latex_to_unicode(s):
    """Convert common LaTeX accent/special commands to Unicode."""
    if not s:
        return s

    # Dotless-i shortcuts: {\'\i} {\'{\i}}
    s = re.sub(r"\{\\'\{?\\i\}?\}", "í", s)
    s = re.sub(r"\{\\`\{?\\i\}?\}", "ì", s)

    # All accent patterns, from most-specific to least-specific
    CMDS = r"'`\^\"~vcuH=\.k"
    # {\'{o}} — accent + braced letter, wrapped in outer braces
    s = re.sub(
        r"\{\\([" + CMDS + r"])\{([a-zA-Z])\}\}",
        lambda m: _sub_accent(m.group(1), m.group(2)),
        s,
    )
    # \'{i} — accent + braced letter, NO outer braces (e.g. Mart\'{i}nez)
    s = re.sub(
        r"\\([" + CMDS + r"])\{([a-zA-Z])\}",
        lambda m: _sub_accent(m.group(1), m.group(2)),
        s,
    )
    # {\'o} — accent + bare letter in braces
    s = re.sub(
        r"\{\\([" + CMDS + r"])([a-zA-Z])\}",
        lambda m: _sub_accent(m.group(1), m.group(2)),
        s,
    )
    # \'o — accent + bare letter, no braces at all
    s = re.sub(
        r"\\([" + CMDS + r"])([a-zA-Z])",
        lambda m: _sub_accent(m.group(1), m.group(2)),
        s,
    )

    # Named special chars (with or without surrounding braces)
    specials = [
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
    ]
    for pat, repl in specials:
        s = re.sub(pat, repl, s)

    # Strip remaining brace pairs (nested too)
    for _ in range(6):
        prev = s
        s = re.sub(r"\{([^{}]*)\}", r"\1", s)
        if s == prev:
            break

    # Typographic substitutions
    s = s.replace("---", "—").replace("--", "–")
    s = re.sub(r"~", " ", s)

    return s.strip()


# ─── BibTeX Sanity Checks ────────────────────────────────────────────────────

REQUIRED_FIELDS = {
    "article": {"author", "title", "journal", "year"},
    "book": {"title", "publisher", "year"},  # author OR editor
    "inproceedings": {"author", "title", "booktitle", "year"},
    "incollection": {"author", "title", "booktitle", "publisher", "year"},
    "proceedings": {"title", "year"},
    "phdthesis": {"author", "title", "school", "year"},
    "mastersthesis": {"author", "title", "school", "year"},
    "techreport": {"author", "title", "institution", "year"},
    "unpublished": {"author", "title", "note"},
    "misc": set(),
}


def check_bib(entries, filename):
    """Print bibtex2html-style warnings for a list of parsed entries."""
    warnings = []
    seen_keys = {}

    for e in entries:
        key = e["ID"]
        etype = e["ENTRYTYPE"].lower()

        # Duplicate key
        if key in seen_keys:
            warnings.append(f"  Repeated entry: {key}")
        seen_keys[key] = True

        # Required fields
        required = REQUIRED_FIELDS.get(etype, set())
        for f in required:
            if not e.get(f, "").strip():
                # book allows author OR editor
                if etype == "book" and f == "author" and e.get("editor", "").strip():
                    continue
                warnings.append(f"  {key}: empty or missing field '{f}'")

        # number without volume
        if e.get("number", "").strip() and not e.get("volume", "").strip():
            if etype not in ("techreport", "misc"):
                warnings.append(f"  {key}: has 'number' but no 'volume'")

        # Empty field values (non-critical, warn for common fields)
        for f in ("booktitle", "journal", "institution", "school"):
            if f in e and not e[f].strip():
                warnings.append(f"  {key}: empty field '{f}'")

    if warnings:
        print(f"\nWarnings for {filename}:", file=sys.stderr)
        for w in warnings:
            print(w, file=sys.stderr)
    else:
        print(f"  {filename}: no issues found", file=sys.stderr)

    return len(warnings)


# ─── Entry Rendering ─────────────────────────────────────────────────────────


def format_authors(raw):
    """'Last, First and Last2, First2' → 'First Last, First2 Last2'"""
    if not raw:
        return ""
    authors = [a.strip() for a in re.split(r"\s+and\s+", raw, flags=re.IGNORECASE)]
    out = []
    for a in authors:
        a = latex_to_unicode(a)
        if "," in a:
            parts = a.split(",", 1)
            a = parts[1].strip() + " " + parts[0].strip()
        out.append(a)
    if len(out) > 6:
        return ", ".join(out[:6]) + " et al."
    return ", ".join(out)


def entry_year(e):
    return e.get("year", "").strip() or "0"


def entry_venue(e):
    """Return a concise venue string."""
    etype = e["ENTRYTYPE"].lower()
    parts = []
    if etype in ("article",):
        if e.get("journal"):
            parts.append(latex_to_unicode(e["journal"]))
        if e.get("volume"):
            vol = e["volume"]
            num = e.get("number", "")
            parts.append(f"Vol. {vol}" + (f"({num})" if num else ""))
        if e.get("pages"):
            parts.append(f"pp. {e['pages']}")
    elif etype in ("inproceedings", "conference"):
        if e.get("booktitle"):
            parts.append(latex_to_unicode(e["booktitle"]))
        if e.get("pages"):
            parts.append(f"pp. {e['pages']}")
    elif etype == "proceedings":
        if e.get("booktitle"):
            parts.append(latex_to_unicode(e["booktitle"]))
    elif etype in ("phdthesis", "mastersthesis"):
        label = "PhD thesis" if etype == "phdthesis" else "Master's thesis"
        if e.get("school"):
            parts.append(f"{label}, {latex_to_unicode(e['school'])}")
        else:
            parts.append(label)
    elif etype == "techreport":
        parts.append("Technical Report")
        if e.get("institution"):
            parts.append(latex_to_unicode(e["institution"]))
    elif etype == "book":
        if e.get("publisher"):
            parts.append(latex_to_unicode(e["publisher"]))
    elif etype in ("misc", "unpublished"):
        if e.get("howpublished"):
            parts.append(latex_to_unicode(e["howpublished"]))
        elif e.get("note"):
            n = latex_to_unicode(e["note"])
            if len(n) < 80:
                parts.append(n)
    if e.get("publisher") and etype not in ("book", "techreport"):
        pub = latex_to_unicode(e.get("publisher", ""))
        if pub and pub not in " ".join(parts):
            parts.append(pub)
    return " · ".join(parts) if parts else ""


def entry_links(e):
    """Return list of (label, url, css_class) for DOI/URL/arXiv."""
    links = []
    doi = e.get("doi", "").strip()
    url = e.get("url", "").strip()
    eprint = e.get("eprint", "").strip()

    if doi:
        doi_url = doi if doi.startswith("http") else f"https://doi.org/{doi}"
        # Detect arXiv DOIs
        if "arxiv" in doi.lower():
            links.append(("arXiv", doi_url, "badge-arxiv"))
        else:
            links.append(("DOI", doi_url, "badge-doi"))

    if url:
        # Don't duplicate an arXiv link we already have from DOI
        if "arxiv.org" in url.lower() and any(lnk[2] == "badge-arxiv" for lnk in links):
            pass
        elif url != (f"https://doi.org/{doi}" if doi else ""):
            if "arxiv.org" in url.lower():
                links.append(("arXiv", url, "badge-arxiv"))
            else:
                links.append(("URL", url, "badge-url"))

    if eprint and not any("arxiv" in lnk[1].lower() for lnk in links):
        links.append(("arXiv", f"https://arxiv.org/abs/{eprint}", "badge-arxiv"))

    return links


def has_pdf(e):
    return bool(e.get("file", "").strip())


def build_entry_json(e):
    """Build a JSON-serialisable dict for one entry (used by the JS renderer)."""
    key = e["ID"]
    etype = e["ENTRYTYPE"]
    year = entry_year(e)
    authors_raw = e.get("author", e.get("editor", ""))
    authors = format_authors(authors_raw)
    title = latex_to_unicode(e.get("title", ""))
    venue = entry_venue(e)
    abstract = latex_to_unicode(e.get("abstract", ""))
    links = entry_links(e)
    pdf = has_pdf(e)
    raw = e["_raw"]

    # Search text (lowercase for JS matching)
    search_text = " ".join(
        [
            key.lower(),
            year,
            authors.lower(),
            title.lower(),
            venue.lower(),
            abstract.lower(),
            etype.lower(),
        ]
    )

    return {
        "key": key,
        "type": etype,
        "year": year,
        "authors": authors,
        "title": title,
        "venue": venue,
        "abstract": abstract,
        "links": links,
        "pdf": pdf,
        "search": search_text,
        "raw": raw,
    }


# ─── HTML Generation ─────────────────────────────────────────────────────────

NAV_PAGES = [
    ("index.html", "OMR Research"),
    ("omr-related-research.html", "Related Research"),
    ("omr-research-unverified.html", "Unverified"),
]


def render_page(title, entries, active_page, output_path):
    """Render a complete interactive HTML page for a bib file."""
    entry_data = [build_entry_json(e) for e in entries]

    # Unique years and types for filter dropdowns
    years = sorted({e["year"] for e in entry_data if e["year"] != "0"}, reverse=True)
    types = sorted({e["type"] for e in entry_data})

    nav_links = "\n".join(
        f'<td><a href="{href}" class="btn-nav{"  btn-nav-active" if href == active_page else ""}">{label}</a></td>'
        for href, label in NAV_PAGES
    )

    entries_json = json.dumps(entry_data, ensure_ascii=False)
    years_options = "\n".join(f'<option value="{y}">{y}</option>' for y in years)
    types_options = "\n".join(f'<option value="{t}">{t}</option>' for t in types)

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html_mod.escape(title)}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Open+Sans">
<style>
/* ── Reset & Base ── */
*, *::before, *::after {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: "Open Sans", Arial, sans-serif; font-size: 1rem; background: #f8f9fa; color: #212529; }}
a {{ color: #155799; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}

/* ── Header ── */
.page-header {{
  padding: 40px 20px 24px;
  color: #fff;
  text-align: center;
  background: linear-gradient(120deg, #155799, #159957);
}}
.page-header h1 {{ margin: 0 0 6px; font-size: 42px; font-weight: 700; }}
.page-header p  {{ margin: 0 0 14px; opacity: 0.85; }}
.btn-github {{
  display: inline-block; padding: 0.75rem 1rem; margin-bottom: 1rem;
  color: rgba(255,255,255,0.7); background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.2); border-radius: 0.3rem;
  transition: color 0.2s, background-color 0.2s, border-color 0.2s;
}}
.btn-github:hover {{ background: rgba(255,255,255,0.2); text-decoration: none; color: #fff; }}
.nav-table {{ margin: 0 auto; border-spacing: 0; }}
.nav-table td {{ padding: 4px 6px; }}
.btn-nav {{
  display: inline-block; padding: 0.75rem 1rem; margin-bottom: 1rem;
  color: rgba(255,255,255,0.7); border-radius: 0.3rem;
  transition: color 0.2s, background-color 0.2s, border-color 0.2s;
}}
.btn-nav:hover {{ background: rgba(255,255,255,0.15); color: #fff; text-decoration: none; }}
.btn-nav-active {{ background: rgba(255,255,255,0.2); color: #fff; font-weight: 600; }}

/* ── Controls ── */
.controls {{
  display: flex; flex-wrap: wrap; gap: 10px; align-items: center;
  padding: 10px 20px; background: #fff; border-bottom: 1px solid #dee2e6;
  position: sticky; top: 0; z-index: 100; box-shadow: 0 1px 4px rgba(0,0,0,.06);
}}
.controls input[type=search], .controls select {{
  font-family: inherit; font-size: inherit;
  padding: 5px 10px; border: 1px solid #ced4da; border-radius: 4px;
  background: #fff; outline: none;
}}
.controls input[type=search] {{ flex: 1 1 200px; min-width: 160px; }}
.controls input[type=search]:focus {{ border-color: #159957; box-shadow: 0 0 0 2px rgba(21,153,87,.15); }}
.controls select {{ cursor: pointer; }}
.controls label {{ color: #555; white-space: nowrap; }}
.stat-label {{ color: #666; white-space: nowrap; }}

/* ── Entry List ── */
.entry-list {{ padding: 12px 20px; max-width: 1100px; margin: 0 auto; }}
.entry-card {{
  background: #fff; border: 1px solid #e1e4e8; border-radius: 6px;
  margin-bottom: 10px; overflow: hidden; cursor: pointer;
  transition: box-shadow 0.15s;
}}
.entry-card:hover {{ box-shadow: 0 2px 8px rgba(0,0,0,.1); }}

.entry-header {{
  padding: 12px 14px 10px;
}}
.entry-chips {{ display: flex; flex-wrap: wrap; align-items: center; gap: 5px; margin-bottom: 4px; }}
.entry-year {{
  font-size: 0.75rem; font-weight: 700; color: #fff;
  background: #159957; padding: 2px 7px; border-radius: 3px;
}}
.entry-type {{
  font-size: 0.75rem; color: #666; background: #f0f0f0;
  padding: 2px 7px; border-radius: 3px; text-transform: lowercase;
}}
.entry-authors {{ color: #555; margin-bottom: 3px; }}
.entry-title {{ font-weight: 600; color: #155799; margin-bottom: 4px; line-height: 1.4; }}
.entry-title a {{ color: #155799; }}
.entry-title a:hover {{ color: #159957; }}
.entry-venue {{ color: #666; margin-bottom: 0; font-style: italic; }}
.badge {{
  display: inline-block; font-size: 0.75rem; font-weight: 700; padding: 2px 7px;
  border-radius: 3px; text-decoration: none; transition: opacity 0.15s;
}}
.badge:hover {{ opacity: 0.8; text-decoration: none; }}
.badge-doi   {{ background: #dbeafe; color: #1e40af; }}
.badge-arxiv {{ background: #fef3c7; color: #92400e; }}
.badge-url   {{ background: #d1fae5; color: #065f46; }}

/* ── Expandable panel ── */
.entry-panel {{
  display: none; border-top: 1px solid #e9ecef; background: #f8f9fa;
}}
.entry-panel.open {{ display: block; }}
.entry-abstract {{
  padding: 10px 14px; line-height: 1.6; color: #333;
  border-bottom: 1px solid #e9ecef;
}}
.entry-bibtex-wrap {{
  position: relative; padding: 10px 14px;
}}
.entry-bibtex {{
  font-family: "Courier New", monospace; font-size: 0.8rem;
  white-space: pre-wrap; word-break: break-all; color: #333; margin: 0;
}}
.copy-btn {{
  position: absolute; top: 10px; right: 14px;
  font-family: inherit; font-size: 0.75rem; cursor: pointer;
  padding: 3px 10px; border-radius: 4px; border: 1px solid #ced4da;
  background: #fff; color: #555; transition: background 0.15s, color 0.15s;
}}
.copy-btn:hover {{ background: #159957; color: #fff; border-color: #159957; }}
.copy-btn.copied {{ background: #159957; color: #fff; border-color: #159957; }}

.no-results {{ text-align: center; color: #888; padding: 40px; }}
</style>
</head>
<body>

<section class="page-header">
  <h1>Bibliography on Optical Music Recognition</h1>
  <p>Last updated: {TODAY}</p>
  <a href="https://github.com/OMR-Research/omr-research.github.io" class="btn-github">View on GitHub</a>
  <table class="nav-table"><tr>{nav_links}</tr></table>
</section>

<div class="controls" id="controls">
  <input type="search" id="q" placeholder="Search title, author, abstract, key…" oninput="applyFilters()">
  <select id="fYear" onchange="applyFilters()">
    <option value="">All years</option>
    {years_options}
  </select>
  <select id="fType" onchange="applyFilters()">
    <option value="">All types</option>
    {types_options}
  </select>
  <label>
    <input type="checkbox" id="fAbstract" onchange="applyFilters()"> Has abstract
  </label>
  <label>Sort:
    <select id="fSort" onchange="applyFilters()">
      <option value="year_desc">Year ↓</option>
      <option value="year_asc">Year ↑</option>
      <option value="author">Author A–Z</option>
      <option value="key">Key A–Z</option>
    </select>
  </label>
  <span class="stat-label" id="statLabel"></span>
</div>

<div class="entry-list" id="entryList"></div>

<script>
const ENTRIES = {entries_json};

let filtered = [];

function esc(s) {{
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}

function renderEntry(e) {{
  const linkHtml = e.links.map(([label,url,cls]) =>
    `<a class="badge ${{cls}}" href="${{esc(url)}}" target="_blank" rel="noopener" onclick="event.stopPropagation()">${{esc(label)}}</a>`
  ).join('');

  const titleHtml = e.links[0]
    ? `<a href="${{esc(e.links[0][1])}}" target="_blank" rel="noopener" onclick="event.stopPropagation()">${{esc(e.title)}}</a>`
    : esc(e.title);

  const absBlock = e.abstract
    ? `<div class="entry-abstract">${{esc(e.abstract)}}</div>`
    : '';

  return `
<div class="entry-card" id="card-${{esc(e.key)}}" onclick="toggleCard(this)">
  <div class="entry-header">
    <div class="entry-chips">
      <span class="entry-year">${{esc(e.year)}}</span>
      <span class="entry-type">${{esc(e.type)}}</span>
      ${{linkHtml}}
    </div>
    <div class="entry-authors">${{esc(e.authors)}}</div>
    <div class="entry-title">${{titleHtml}}</div>
    ${{e.venue ? `<div class="entry-venue">${{esc(e.venue)}}</div>` : ''}}
  </div>
  <div class="entry-panel" id="panel-${{esc(e.key)}}">
    ${{absBlock}}
    <div class="entry-bibtex-wrap">
      <button class="copy-btn" onclick="copyBib(event, this, '${{esc(e.key)}}')">Copy BibTeX</button>
      <pre class="entry-bibtex" id="bib-${{esc(e.key)}}">${{esc(e.raw.trim())}}</pre>
    </div>
  </div>
</div>`;
}}

function toggleCard(card) {{
  const panel = card.querySelector('.entry-panel');
  panel.classList.toggle('open');
}}

function copyBib(event, btn, key) {{
  event.stopPropagation();
  const text = document.getElementById('bib-' + key).textContent;
  navigator.clipboard.writeText(text).then(() => {{
    btn.textContent = 'Copied!';
    btn.classList.add('copied');
    setTimeout(() => {{ btn.textContent = 'Copy BibTeX'; btn.classList.remove('copied'); }}, 1800);
  }});
}}

function sortEntries(arr, mode) {{
  return arr.slice().sort((a,b) => {{
    if (mode === 'year_desc') return (b.year||'0').localeCompare(a.year||'0') || a.key.localeCompare(b.key);
    if (mode === 'year_asc')  return (a.year||'0').localeCompare(b.year||'0') || a.key.localeCompare(b.key);
    if (mode === 'author')    return a.authors.localeCompare(b.authors) || (b.year||'0').localeCompare(a.year||'0');
    if (mode === 'key')       return a.key.localeCompare(b.key);
    return 0;
  }});
}}

function applyFilters() {{
  const q    = document.getElementById('q').value.toLowerCase();
  const yr   = document.getElementById('fYear').value;
  const tp   = document.getElementById('fType').value;
  const abs  = document.getElementById('fAbstract').checked;
  const sort = document.getElementById('fSort').value;

  filtered = ENTRIES.filter(e => {{
    if (q  && !e.search.includes(q)) return false;
    if (yr && e.year !== yr)         return false;
    if (tp && e.type !== tp)         return false;
    if (abs && !e.abstract)          return false;
    return true;
  }});

  filtered = sortEntries(filtered, sort);

  const list = document.getElementById('entryList');
  if (filtered.length === 0) {{
    list.innerHTML = '<p class="no-results">No entries match the current filters.</p>';
  }} else {{
    list.innerHTML = filtered.map(renderEntry).join('');
  }}

  document.getElementById('statLabel').textContent =
    `${{filtered.length}} of ${{ENTRIES.length}} entries`;
}}

// Initial render
applyFilters();
</script>
</body>
</html>
"""
    Path(output_path).write_text(page, encoding="utf-8")
    print(f"  Written {output_path}  ({len(entries)} entries)")


# ─── Main ────────────────────────────────────────────────────────────────────


def main():
    check_only = "--check" in sys.argv
    print("OMR Research site generator", file=sys.stderr)
    print("=" * 40, file=sys.stderr)

    total_warnings = 0

    configs = [
        ("OMR-Research.bib", "Bibliography on Optical Music Recognition", "index.html"),
        (
            "OMR-Related-Research.bib",
            "Related Research — Bibliography on OMR",
            "omr-related-research.html",
        ),
        (
            "OMR-Research-Unverified.bib",
            "Unverified Research — Bibliography on OMR",
            "omr-research-unverified.html",
        ),
    ]

    for bib_file, page_title, out_file in configs:
        bib_path = BASE / bib_file
        if not bib_path.exists():
            print(f"  SKIP: {bib_file} not found", file=sys.stderr)
            continue

        print(f"\nProcessing {bib_file}...", file=sys.stderr)
        entries = parse_bib(bib_path)
        print(f"  Parsed {len(entries)} entries", file=sys.stderr)

        total_warnings += check_bib(entries, bib_file)

        if not check_only:
            render_page(page_title, entries, out_file, BASE / out_file)

    if check_only:
        print(f"\nTotal warnings: {total_warnings}", file=sys.stderr)
        sys.exit(1 if total_warnings else 0)

    # Remove obsolete pages left over from old bibtex2html pipeline
    for obsolete in ("omr-research-compact.html", "omr-research-sorted-by-key.html"):
        p = BASE / obsolete
        if p.exists():
            p.unlink()
            print(f"  Removed obsolete: {obsolete}")

    print("\nDone.", file=sys.stderr)


if __name__ == "__main__":
    main()
