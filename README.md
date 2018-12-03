# [Music Recognition Research Bibliography](https://omr-research.github.io/)

Build the website on Windows using the command 

```
BibTeX2HTML\Windows\bibtex2html.exe --use-keys --no-keywords --nodoc -a -o OMR-Research-Key .\OMR-Research.bib
BibTeX2HTML\Windows\bibtex2html.exe --use-keys --no-keywords --nodoc -d -o OMR-Research-Year .\OMR-Research.bib
BibTeX2HTML\Windows\bibtex2html.exe --use-keys --no-keywords --nodoc -a -noabstract -o OMR-Research-Compact .\OMR-Research.bib

copy Header.html + OMR-Research-Key.html + Footer.html index.html /Y
copy Header.html + OMR-Research-Year.html + Footer.html index-year.html /Y
copy Header.html + OMR-Research-Compact.html + Footer.html index-compact.html /Y

del OMR-Research-Key.html
del OMR-Research-Year.html
del OMR-Research-Compact.html
```
