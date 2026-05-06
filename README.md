# [Optical Music Recognition Research Bibliography](https://omr-research.github.io/)

This repository contains the most extensive, curated bibliography on Optical Music Recognition. It contains three different BibTex files that are the authoritative sources from which the website [https://omr-research.github.io/](https://omr-research.github.io/) will be generated.

1. **OMR Research Bibliography**: A collection of scientific and technical publications, that were manually verified for correctness from a trustworthy source (see below). Most of these entries have either a Digital Object Identifier (DOI) or a link to the website, where the publication can be found.
2. **OMR Related Bibliography**: A collection of scientific and technical publications, that were manually verified for correctness from a trustworthy source but are not primarily directly towards Optical Music Recognition, such as musicological research or general computer vision papers.
3. **Unverified OMR Bibliography**: A collection of scientific and technical publications, that are related to Optical Music Recognition, but they could not be verified from a trustworthy source and might contain incorrect information. Many publications from this collection were authored before 1990 and are often not indexed by the search engines or the respective proceedings could no longer be accessed and verified by us.

# Acquisition and Verification Process
The bibliography was acquired and merged from multiple sources, such as the public and private
collections from multiple researchers that have historically grown, including a recent one by Andrew
Hankinson, who provided us with an extensive BibTeX library. Additionally, we have a Google Scholar
Alert on Ana Rebelo's "Optical music recognition: state-of-the-art and open issues" as it currently represents the latest survey and is cited by almost every publication.

To verify the information of each entry in the bibliography, we proceeded with the following steps:

1. Search on Google Scholar for the title of the work, if necessary with the authors last name and the
year of publication.
2. Find a trustworthy source such as the original publisher, the authors’ website, the website of the venue
(that lists the article in the program) or indexing services including IEEE Xplore Digital Library,
ACM Digital Library, Springer Link, Elsevier ScienceDirect, arXiv.org, dblp.org or ResearchGate.
Information from the last three services are used with caution and if possible backed up with
information from other sources.
3. Manually verify the correctness of the metadata by inspecting and correcting it with the necessary
information from another source, e.g., the conference website or the information stated in the document.
Suspicious information could be if the author’s name is missing letters that were lost due to special characters;
or if the year of publication is before that of cited references.

Once we verified the entry, we add it to the respective bibliography with [JabRef](http://www.jabref.org/)
and link the original PDF file or at least the DOI. Articles that were only found as PDF without the
associated venue of publication were classified as technical reports. Bachelor theses and online sources
such as websites of commercial applications were classified as ’Misc’ because of the lack of an appropriate
category in BibTex.

## Updating the BibTex files

If you find [an error](https://github.com/OMR-Research/omr-research.github.io/issues/new?template=incorrect-entry.md) in any of the three BibTex files or want to [add a missing entry](https://github.com/OMR-Research/omr-research.github.io/issues/new?template=missing-entry.md), please open an [issue](https://github.com/OMR-Research/omr-research.github.io/issues/new/choose). Especially many old entries could not be verified by us and we appreciate any help from the community to keep this bibliography updated, accessible and a useful resource for the entire community.

## Building the website

The website is generated from the three BibTeX files using a Python script. No external tools (LaTeX, BibTeX, bibtex2html) are required.

**Requirements:** Python 3 (standard library only — no additional packages needed).

### Automated deployment

Pushing to `master` triggers `.github/workflows/deploy.yml`, which runs `generate_site.py` and deploys the output to GitHub Pages automatically. The generated HTML files are not committed to the repository.

> **One-time setup:** In the repository's **Settings → Pages**, set the source to **GitHub Actions** (instead of "Deploy from a branch").

### Generating the HTML files locally

```bash
python3 generate_site.py                # standard output
python3 generate_site.py --pdf-links    # local review: adds a PDF chip to each entry
python3 generate_site.py --check        # sanity-check only, no output files written
```

This produces three HTML files:

| Output file | Source | Description |
|---|---|---|
| `index.html` | `OMR-Research.bib` | Main verified OMR bibliography |
| `omr-related-research.html` | `OMR-Related-Research.bib` | Related (non-OMR-primary) works |
| `omr-research-unverified.html` | `OMR-Research-Unverified.bib` | Unverified entries |

The `--pdf-links` flag adds a red **PDF** badge next to the DOI/arXiv chips for every entry whose `file` field contains a local PDF path (as stored by JabRef). This gives one-click access to the papers when browsing locally. The flag is off by default so the public website is unaffected.

[RenderWebsite.sh](RenderWebsite.sh) is a convenience wrapper that calls the same command.

### Reviewing changes since a baseline commit

`generate_diff_report.py` compares the current `OMR-Research.bib` against any previous commit and writes `diff-report.html` — a browsable report showing new entries and all changed fields (abstracts, PDFs, DOIs, other metadata) side-by-side.

```bash
python3 generate_diff_report.py              # compare against the default baseline (3bb06ea5)
python3 generate_diff_report.py <commit>     # compare against any other commit
```

`diff-report.html` is not committed to the repository.

## Steps for updating the website

Make sure the BibTeX files are correct and push to `master`. The GitHub Actions workflow will rebuild and redeploy the site automatically.
