#!/bin/bash

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
