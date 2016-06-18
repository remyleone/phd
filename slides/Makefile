all:
	latexmk slides.tex

travis:
	pdflatex slides.tex

clean:
	latexmk -C

sync:
	scp slides.pdf perso:html/slides_leone_remy.pdf
