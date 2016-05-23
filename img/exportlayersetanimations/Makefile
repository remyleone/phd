# LaTeX Makefile
# Copyright (C)2006-2011, Jordan Augé <jordan.auge@free.fr>
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA 02110-1301, USA
#
# TODO
#
# - Créer les répertoires s'ils n'existent pas

#
# Directories
#
FIGDIR=figsrc
TMPDIR=fig

FILE=main

VIEWER=okular

.SUFFIXES: .fig .svg .png .eps

#
# .FIG files support
#

FIG=$(wildcard $(FIGDIR)/*.fig)

all: make_figures clean pdf
	#bibtex $(FILE)
	pdflatex $(FILE).tex

make_figures:
	./make_figures.sh

# List of resulting .0 files
$(TMPDIR)/%.mmp : $(FIGDIR)/%.fig
	fig2dev -L mmp $< $@
$(TMPDIR)/%.0 : $(TMPDIR)/%.mmp
	# Fix weirdness in elastic-streaming-flows.fig
	sed -i "s/-81615531.34/0/" $<
	# We should make some sanity checks here (font, etc...)
	mpost $<
	# Move files into $(TMPDIR) since the -output-directory parameter fails
	for i in $*.mpx; do rm -f $$i; done
	for i in $*.mmp.log; do rm $$i; done
	for i in $*.mmp.*; do mv $$i "$(TMPDIR)/$${i%%.mmp*}$${i##$*.mmp}"; done
$(TMPDIR)/%.eps : $(FIGDIR)/%.fig
	@echo "Converting $< to $@ (fig2dev)..."
	@fig2dev -L eps $< $@
$(TMPDIR)/%.pdf : $(FIGDIR)/%.fig
	@echo "Converting $< to $@ (fig2dev)..."
	@fig2dev -L pdf $< $@
TMPEPS+=$(FIG:$(FIGDIR)/%.fig=$(TMPDIR)/%.0)
TMPEPS+=$(FIG:$(FIGDIR)/%.fig=$(TMPDIR)/%.eps)
TMPPDF+=$(FIG:$(FIGDIR)/%.fig=$(TMPDIR)/%.pdf)

#
# svg files support
#
SVG=$(wildcard $(FIGDIR)/*.svg)
$(TMPDIR)/%.eps : $(FIGDIR)/%.svg
	@echo "Converting $< to $@ (inkscape)..."
	@inkscape -z -T -D -E $@ $< 2>&1
$(TMPDIR)/%.pdf : $(TMPDIR)/%.eps
	@echo "Converting $< to $@ (epstopdf)..." # XXX
	@epstopdf $< --outfile $@ 2>&1
$(TMPDIR)/%.jpg : $(FIGDIR)/%.svg
	@echo "Converting $< to $@ (convert)..."
	@inkscape -z -T -D -E $@ $< 2>&1
$(TMPDIR)/%.png : $(FIGDIR)/%.svg
	@echo "Converting $< to $@ (convert)..."
	@inkscape -z -T -D -e $@ $< 2>&1
TMPEPS+=$(SVG:$(FIGDIR)/%.svg=$(TMPDIR)/%.eps)
TMPPDF+=$(SVG:$(FIGDIR)/%.svg=$(TMPDIR)/%.pdf)
TMPJPG+=$(SVG:$(FIGDIR)/%.svg=$(TMPDIR)/%.jpg)
TMPPNG+=$(SVG:$(FIGDIR)/%.svg=$(TMPDIR)/%.png)

#
# png files support
#
PNG=$(wildcard $(FIGDIR)/*.png)
$(TMPDIR)/%.eps : $(FIGDIR)/%.png
	@echo "Converting $< to $@ (convert)..."
	@convert $< $@ 2>&1
$(TMPDIR)/%.pdf : $(FIGDIR)/%.png
	@echo "Converting $< to $@ (convert)..." # XXX
	@convert $< $@ 2>&1
$(TMPDIR)/%.jpg : $(FIGDIR)/%.png
	@echo "Converting $< to $@ (convert)..."
	@convert $< $@ 2>&1
$(TMPDIR)/%.png : $(FIGDIR)/%.png
	@echo "Copying $< to $@..."
	@cp $< $@ 2>&1
TMPEPS+=$(PNG:$(FIGDIR)/%.png=$(TMPDIR)/%.eps)
TMPPDF+=$(PNG:$(FIGDIR)/%.png=$(TMPDIR)/%.pdf)
TMPJPG+=$(PNG:$(FIGDIR)/%.png=$(TMPDIR)/%.jpg)
TMPPNG+=$(PNG:$(FIGDIR)/%.png=$(TMPDIR)/%.png)

#
# eps files support
#
EPS=$(wildcard $(FIGDIR)/*.eps)
$(TMPDIR)/%.eps : $(FIGDIR)/%.eps
	@echo "Copying $< to $@..."
	@cp $< $@ 2>&1
$(TMPDIR)/%.pdf : $(FIGDIR)/%.eps
	@echo "Converting $< to $@ (epstopdf)..." # XXX
	@epstopdf $< --outfile $@ 2>&1
$(TMPDIR)/%.jpg : $(FIGDIR)/%.eps
	@echo "Converting $< to $@ (convert)..."
	@convert $< $@ 2>&1
$(TMPDIR)/%.png : $(FIGDIR)/%.eps
	@echo "Converting $< to $@ (convert)..."
	@convert $< $@ 2>&1
TMPEPS+=$(EPS:$(FIGDIR)/%.eps=$(TMPDIR)/%.eps)
TMPPDF+=$(EPS:$(FIGDIR)/%.eps=$(TMPDIR)/%.pdf)
TMPJPG+=$(EPS:$(FIGDIR)/%.eps=$(TMPDIR)/%.jpg)
TMPPNG+=$(EPS:$(FIGDIR)/%.eps=$(TMPDIR)/%.png)

pspdf: ps
	@ps2pdf $(FILE).ps

pdf: $(TMPPDF)
	pdflatex $(FILE).tex
	bibtex $(FILE)
	pdflatex $(FILE).tex
	pdflatex $(FILE).tex

ps: dvi
	@dvips -R0 $(FILE).dvi
	#@dvips -R0 -Ppdf $(FILE).dvi

dvi: $(TMPEPS)
	#@latex $(FILE).tex
	#@bibtex $(FILE)
	#@latex $(FILE).tex
	@latex $(FILE).tex

view:
	@$(VIEWER) $(FILE).pdf

clean:
	@rm -Rf $(FILE).bbl $(FILE).blg $(FILE).aux $(FILE).log $(FILE).toc $(FILE).dvi $(FILE).snm $(FILE).nav $(FILE).out $(FILE).vrb

cleanall: clean
	@rm -Rf $(FILE).ps $(FILE).pdf $(TMPDIR)/*

png: $(TMPPNG)

eps: $(TMPEPS)

pdf: $(TMPPDF)

jpg: $(TMPJPG)

#
# Slides specific
#
handout.tex: $(FILE).tex
	sed 's/documentclass/&[handout]/' $(FILE).tex > handout.tex

handout: handout.pdf
	pdfnup --nup 2x2 --paper a4paper --orient landscape --frame true --scale 0.96 --delta "2mm 2mm" handout.pdf

#
# SVN
#
archive:
	@echo "TODO: Create an archive of current files"

commit:
	@echo "TODO: Commit changes to subversion server"

new:
	@echo "TODO: Create a new empty report (must ensure the directory is empty except this Makefile)"

toc:
	@grep section main.tex | sed "s/.*subsubsection.*{\(.*\)}.*/    \1/" | sed "s/.*subsection.*{\(.*\)}.*/  \1/" | sed "s/.*section.*{\(.*\)}.*/\1/"
