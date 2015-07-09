# phd

This repository contains all the source code to generate my PhD manuscript. All 
this code is managed though git and tested on travis-ci.

## Code Status

![Build Status](https://api.travis-ci.com/sieben/phd.svg?token=MptuivNtDqJAT7p4miJw)

TL;DR: There are several tools to help you make good LaTeX. This repo can be used as a template for a PhD thesis. 
Especially for [Edite](https://edite-de-paris.fr) students.

## LaTeX tools

### Nag

[Nag](//www.ctan.org/tex-archive/macros/latex/contrib/nag) is a tool to help
you detect old commands and deprecated LaTeX code.

Simply put the following lines in your code:

``` latex
\usepackage[l2tabu, orthodox]{nag}
```

### latexmk

[Latexmk](//users.phys.psu.edu/~collins/software/latexmk-jcc/) is a very good
tool to never have to worry anymore about how many time you have to compile to
get your bibliography right. A latemkrc is the file you will put inside the
project that will help bootstrap latexmk. Here's mine:

``` perl
$pdf_mode = "1";
$pdflatex = "pdflatex";
$makeindex = "splitindex";
$makeindex = "makeindex;splitindex;";
```

## Spelling help

### Language tool

[Language tool](//languagetool.org) is Java grammar checker. It helps detect
grammar mistakes such as _He play tennis_ and many others. I usually launch
the checker against all my tex folder. I got a make command to help me go it
quickly:

	make grammar_check

### Pandoc + Microsoft Office

[Pandoc](//johnmacfarlane.net/pandoc) is like a swiss-army knife for
converting text back and forth in different format.

Suppose that you have a large body of text in LaTeX and you want to convert it
to a docx format to spell check it on Microsoft Office. By using pandoc you
could have it quickly:

	pandoc main.tex -o main.docx

That's it! Now, you have a main.docx that you can pass along to other grammar
checker such as the one embedded in Microsoft Word.

## Project layout

I like to have a modular project. Therefore, I use the following layout:


	├── myproject.sublime-project
	├── myproject.sublime-workspace
	├── IEEEtran.cls
	├── latexmkrc
	├── main.pdf
	├── main.tex
	├── Makefile
	├── readme.md
	├── main.bib
	└── tex
	    ├── abstract.tex
	    ├── conclusion.tex
	    ├── experiment.tex
	    ├── intro.tex
	    └── related.tex

A main.tex document that import all other using similar snippets:

``` latex
\begin{document}

\maketitle

\input{tex/abstract}
\input{tex/intro}
\input{tex/related}
\input{tex/experiment}
\input{tex/conclusion}

\end{document}
```

Organizing code this way is handy because I only have small files that I can
easily get on one screen, share in an email or simply read in one sight. If my
code was a monolithic file with thoushands of lines, it would be much harder
to see where I am in the structure.

Plus if you use an editor such as [Vim](//www.vim.org) (plus the Ctrl-p
plugin) or [Sublime Text](//sublimetext.com) you can open any file you want by
simply typing Ctrl-p and going in very few key strokes anywhere in your
document.

### Makefile

Of course, you don't want to type commands all the time. Therefore you put
them in a makefile like this one:

``` makefile
LT_DL=https://languagetool.org/download/LanguageTool-2.8.zip
LT_FOLDER=~/lt
LT=~/lt/LanguageTool-2.8/languagetool-commandline.jar

all:
        latexmk

clean:
        latexmk -C

grammar_check:
        java -jar $(LT) -r tex

fetch_grammar_check:
        wget $(LT_DL) -O $(LT_FOLDER).zip
        unzip $(LT_FOLDER).zip -d $(LT_FOLDER)
``` 

## Thanks do you have a nice bundle with all those tools?

Go check it out at the following [address](//github.com/sieben/latex).

To install Language tool just type:

	make fetch_grammar_check

It will download and unzip in your home the grammar checker.

Simply type make to compile your document and make check to do your spell checking.
