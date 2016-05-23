all:
	latexmk main.tex

travis:
	pdflatex main.tex

clean:
	rm -f *.mtc *.mtc0 *.mtc1 *.mtc10 *.mtc2 *.mtc3
	rm -f *.mtc4 *.mtc5 *.mtc6 *.mtc7 *.mtc8 *.mtc9
	rm -f *.log *.bbl *.blg *.fls *.lof *.maf *.toc
	latexmk -C

sync:
	rsync -Pizav . perso:html/
	echo "http://leone.iiens.net/phd_leone_remy.pdf"

word:
	pandoc main.tex -o main.docx

grammar_check:
	find tex -name '*.tex' ! -name '*Bibliography.tex' ! -name '*config.tex' ! -name '*Contents.tex' -exec java -jar $(LT) -l $(LT_LANG) -d $(LT_IGNORE) {} \;

fetch_grammar_check:
	wget $(LT_DL) -O $(LT_FOLDER).zip
	unzip $(LT_FOLDER).zip -d $(LT_FOLDER)
