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
