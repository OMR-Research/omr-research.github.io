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
First, update the date in the [header](template/Header.html), then follow the remaining instructions below. 

Make sure you have LaTeX/BibTex installed and available on your commandline. We recommend installing it via [MikTex](https://miktex.org/).

### Windows

You can build the website on Windows using the following commands 

```
del *.html

BibTeX2HTML\Windows\bibtex2html.exe -s omr-style --use-keys --no-keywords --nodoc -o OMR-Research-Key OMR-Research.bib
BibTeX2HTML\Windows\bibtex2html.exe -s omr-style --use-keys --no-keywords --nodoc -d -r -o OMR-Research-Year OMR-Research.bib
BibTeX2HTML\Windows\bibtex2html.exe -s omr-style --use-keys --no-keywords --nodoc -noabstract -o OMR-Research-No-Abstract OMR-Research.bib
BibTeX2HTML\Windows\bibtex2html.exe -s omr-style --use-keys --no-keywords --nodoc -o OMR-Related-Research OMR-Related-Research.bib
BibTeX2HTML\Windows\bibtex2html.exe -s omr-style --use-keys --no-keywords --nodoc -o OMR-Unverified OMR-Research-Unverified.bib

copy template\Header.html + OMR-Research-Key.html + template\Footer.html index.html /Y
copy template\Header.html + OMR-Research-Year.html + template\Footer.html omr-research-sorted-by-year.html /Y
copy template\Header.html + OMR-Research-No-Abstract.html + template\Footer.html omr-research-compact.html /Y
copy template\Header.html + OMR-Related-Research.html + template\Footer.html omr-related-research.html /Y
copy template\Header.html + OMR-Unverified.html + template\Footer.html omr-research-unverified.html /Y

del OMR-Research-Key.html
del OMR-Research-Year.html
del OMR-Research-No-Abstract.html
del OMR-Related-Research.html
del OMR-Unverified.html

```

[RenderWebsite.bat](RenderWebsite.bat) contains exactly the same commands for easier execution.

We recommend that you remove the trailing special character from the generated omr-research*.html websites (caused by bibtex2html) before committing.


### MacOS

You can build the website on MacOS using the following commands 

```
rm *.html

BibTeX2HTML/OSX_x86_64/bibtex2html -s omr-style --use-keys --no-keywords --nodoc -o OMR-Research-Key OMR-Research.bib
BibTeX2HTML/OSX_x86_64/bibtex2html -s omr-style --use-keys --no-keywords --nodoc -d -r -o OMR-Research-Year OMR-Research.bib
BibTeX2HTML/OSX_x86_64/bibtex2html -s omr-style --use-keys --no-keywords --nodoc -noabstract -o OMR-Research-No-Abstract OMR-Research.bib
BibTeX2HTML/OSX_x86_64/bibtex2html -s omr-style --use-keys --no-keywords --nodoc -o OMR-Related-Research OMR-Related-Research.bib
BibTeX2HTML/OSX_x86_64/bibtex2html -s omr-style --use-keys --no-keywords --nodoc -o OMR-Unverified OMR-Research-Unverified.bib

cat template/Header.html OMR-Research-Key.html template/Footer.html > index.html
cat template/Header.html OMR-Research-Year.html template/Footer.html > omr-research-sorted-by-year.html
cat template/Header.html OMR-Research-No-Abstract.html template/Footer.html > omr-research-compact.html
cat template/Header.html OMR-Related-Research.html template/Footer.html > omr-related-research.html
cat template/Header.html OMR-Unverified.html template/Footer.html > omr-research-unverified.html

rm OMR-Research-Key.html
rm OMR-Research-Year.html
rm OMR-Research-No-Abstract.html
rm OMR-Related-Research.html
rm OMR-Unverified.html
```

[RenderWebsite.sh](RenderWebsite.sh) contains exactly the same commands for easier execution.

### Linux
The same process should also be available under Linux with the binaries of bibtex2html residing in `BibTeX2HTML\Linux` but are currently not tested.

## Steps for updating the website

To update the rendered html, firstly make sure that the BibTex-files are updated and correct. Then you can execute the commands from above to build the HTML files that will be committed directly into the repository along with the generated content. 
