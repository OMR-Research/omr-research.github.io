# [Optical Music Recognition Research Bibliography](https://omr-research.github.io/)

This repository contains the most extensive, curated bibliography on Optical Music Recognition. It contains three different BibTex files that are the authoritative sources from which the website [https://omr-research.github.io/](https://omr-research.github.io/) will be generated.

1. **OMR Research Bibliography**: A collection of scientific and technical publications, that were manually verified for correctness from a trustworthy source (see below). Most of these entries have either a Digital Object Identifier (DOI) or a link to the website, where the publication can be found.
2. **OMR Related Bibliography**: A collection of scientific and technical publications, that were manually verified for correctness from a trustworthy source but are not primarily directly towards Optical Music Recognition, such as musicological research or general computer vision papers.
3. **Unverified OMR Bibliography**: A collection of scientific and technical publications, that are related to Optical Music Recognition, but they could not be verified from a trustworthy source and might contain incorrect information. Many publications from this collection were authored before 1990 and are often not indexed by the search engines or the respective proceedings could no longer be accessed and verified by us.

## Updating the BibTex files

If you find [an error](https://github.com/OMR-Research/omr-research.github.io/issues/new?template=incorrect-entry.md) in any of the three BibTex files or want to [add a missing entry](https://github.com/OMR-Research/omr-research.github.io/issues/new?template=missing-entry.md), please open an [issue](https://github.com/OMR-Research/omr-research.github.io/issues/new/choose). Especially many old entries could not be verified by us and we appreciate any help from the community to keep this bibliography updated, accessible and a useful resource for the entire community.

## Building the website
First update the date in the [header](template/Header.html). 

Make sure you have LaTeX/BibTex installed and available on your commandline. We recommend installing it via [MikTex](https://miktex.org/).

Then you can build the website on Windows using the following commands 

```
del *.html

BibTeX2HTML\Windows\bibtex2html.exe -s omr-style --use-keys --no-keywords --nodoc -o OMR-Research-Key OMR-Research.bib
BibTeX2HTML\Windows\bibtex2html.exe -s omr-style --use-keys --no-keywords --nodoc -d -r -o OMR-Research-Year OMR-Research.bib
BibTeX2HTML\Windows\bibtex2html.exe -s omr-style --use-keys --no-keywords --nodoc -noabstract -o OMR-Research-No-Abstract OMR-Research.bib
BibTeX2HTML\Windows\bibtex2html.exe -s omr-style --use-keys --no-keywords --nodoc -o OMR-Related OMR-Related-Research.bib
BibTeX2HTML\Windows\bibtex2html.exe -s omr-style --use-keys --no-keywords --nodoc -o OMR-Unverified OMR-Research-Unverified.bib

copy template\Header.html + OMR-Research-Key.html + template\Footer.html index.html /Y
copy template\Header.html + OMR-Research-Year.html + template\Footer.html omr-research-sorted-by-year.html /Y
copy template\Header.html + OMR-Research-No-Abstract.html + template\Footer.html omr-research-compact.html /Y
copy template\Header.html + OMR-Related.html + template\Footer.html omr-related-research.html /Y
copy template\Header.html + OMR-Unverified.html + template\Footer.html omr-research-unverified.html /Y

del OMR-Research-Key.html
del OMR-Research-Year.html
del OMR-Research-No-Abstract.html
del OMR-Related.html
del OMR-Unverified.html

```

[RenderWebsite.bat](RenderWebsite.bat) contains exactly the same commands for easier execution.

The same process should also be available under Linux with the binaries of bibtex2html residing in `BibTeX2HTML\Linux` but are currently not tested.

We recommend that you remove the trailing special character from the generated omr-research*.html websites (caused by bibtex2html) before committing.

## Steps for updating the website

To update the rendered html, firstly make sure that the BibTex-files are updated and correct. Then you can execute the commands from above to build the HTML files that will be committed directly into the repository along with the generated content. 
