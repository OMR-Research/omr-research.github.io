#!/usr/bin/env python3
"""
sort_bibtex.py — rewrites each BibTeX file with its entries sorted alphabetically
by citation key.

Entries get pasted in at arbitrary positions over time (for example, a new entry
added at the very top of the file), so the file drifts out of alphabetical order.
This script restores that order without touching entry content, and leaves
JabRef's own "@Comment{jabref-meta: ...}" / "@String" / "@Preamble" blocks
untouched at the end of the file.

Usage:
    python3 sort_bibtex.py           # sort all bibliography files in place
    python3 sort_bibtex.py --check   # exit 1 if any file is not already sorted
"""

import argparse
import re
import sys
from pathlib import Path

BASE = Path(__file__).parent

BIBLIOGRAPHY_FILENAMES = [
    "OMR-Research.bib",
    "OMR-Related-Research.bib",
    "OMR-Research-Unverified.bib",
]

_META_TYPES = {"comment", "string", "preamble"}
_ENTRY_KEY_PATTERN = re.compile(r"@\w+\s*[\{(]\s*([^,\s]+)\s*,")


def split_into_blocks(text: str) -> list[tuple[str, str]]:
    """Split raw BibTeX text into (sort_key, raw_block_text) pairs, in file order.

    A block with a non-empty sort_key is a regular bibliography entry. A block
    with an empty sort_key is a JabRef metadata block (comment/string/preamble),
    which is left in place at the end of the file instead of being reordered.
    """
    blocks = []
    for match in re.finditer(r"@(\w+)\s*[\{(]", text):
        entry_type = match.group(1).lower()
        start = match.start()
        # Only "{" / "}" delimit BibTeX groups; a stray "(" or ")" inside a
        # field value (e.g. an affiliation like "Institute (Country") must not
        # be mistaken for entry nesting.
        depth = 0
        pos = match.end() - 1
        end = len(text)
        while pos < len(text):
            if text[pos] == "{":
                depth += 1
            elif text[pos] == "}":
                depth -= 1
                if depth == 0:
                    end = pos + 1
                    break
            pos += 1

        raw_block_text = text[start:end].strip("\n")
        if entry_type in _META_TYPES:
            blocks.append(("", raw_block_text))
            continue

        key_match = _ENTRY_KEY_PATTERN.match(raw_block_text)
        sort_key = key_match.group(1).strip() if key_match else ""
        blocks.append((sort_key, raw_block_text))
    return blocks


def sort_bibliography_text(text: str) -> str:
    """Return the text with citation-keyed entries sorted alphabetically by key."""
    blocks = split_into_blocks(text)
    entries = [block for block in blocks if block[0]]
    meta_blocks = [block for block in blocks if not block[0]]
    entries.sort(key=lambda block: block[0].casefold())

    sorted_text = "\n\n".join(raw_block_text for _, raw_block_text in entries)
    if meta_blocks:
        sorted_text += "\n\n" + "\n\n".join(
            raw_block_text for _, raw_block_text in meta_blocks
        )
    return sorted_text + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sort BibTeX files alphabetically by citation key."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if any file is not already sorted; do not write changes.",
    )
    args = parser.parse_args()

    found_unsorted_file = False

    for filename in BIBLIOGRAPHY_FILENAMES:
        bibliography_path = BASE / filename
        if not bibliography_path.exists():
            continue

        original_text = bibliography_path.read_text(encoding="utf-8")
        sorted_text = sort_bibliography_text(original_text)

        if sorted_text == original_text:
            continue

        if args.check:
            found_unsorted_file = True
            print(
                f"{filename}: entries are not sorted alphabetically by citation key",
                file=sys.stderr,
            )
        else:
            bibliography_path.write_text(sorted_text, encoding="utf-8")
            print(f"{filename}: sorted", file=sys.stderr)

    if args.check and found_unsorted_file:
        print("\nRun 'python3 sort_bibtex.py' to fix.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
