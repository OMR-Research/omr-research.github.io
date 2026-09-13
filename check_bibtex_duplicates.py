#!/usr/bin/env python3
"""
check_bibtex_duplicates.py — fails if any BibTeX file has duplicate citation keys.

A duplicate citation key breaks the "Copy BibTeX" button on the generated
website, because the button looks up the entry by an HTML element id derived
from the key: with two entries sharing a key, only the first one is ever found.

Usage:
    python3 check_bibtex_duplicates.py
"""

import sys
from pathlib import Path

import generate_site

BASE = Path(__file__).parent

BIBLIOGRAPHY_FILENAMES = [
    "OMR-Research.bib",
    "OMR-Related-Research.bib",
    "OMR-Research-Unverified.bib",
]


def find_duplicate_keys(bibliography_path: Path) -> dict[str, int]:
    """Return each citation key that occurs more than once, with its occurrence count."""
    entries = generate_site.parse_bib(bibliography_path)
    occurrence_count: dict[str, int] = {}
    for entry in entries:
        key = entry["ID"]
        occurrence_count[key] = occurrence_count.get(key, 0) + 1
    return {key: count for key, count in occurrence_count.items() if count > 1}


def main() -> None:
    found_any_duplicate = False

    for filename in BIBLIOGRAPHY_FILENAMES:
        bibliography_path = BASE / filename
        if not bibliography_path.exists():
            continue

        duplicate_keys = find_duplicate_keys(bibliography_path)
        if duplicate_keys:
            found_any_duplicate = True
            print(f"Duplicate citation keys in {filename}:", file=sys.stderr)
            for key, count in sorted(duplicate_keys.items()):
                print(f"  {key} ({count} occurrences)", file=sys.stderr)

    if found_any_duplicate:
        print(
            "\nRename the duplicated keys (e.g. append 'a', 'b', ...) so every "
            "citation key is unique within its file.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("No duplicate citation keys found.", file=sys.stderr)


if __name__ == "__main__":
    main()
