LT_DL=https://languagetool.org/download/LanguageTool-2.8.zip
LT_FOLDER=~/lt
LT=~/lt/LanguageTool-2.8/languagetool-commandline.jar
LT_IGNORE=WHITESPACE_RULE,COMMA_PARENTHESIS_WHITESPACE,EN_UNPAIRED_BRACKETS
LT_LANG=en-US

all:
	latexmk main.tex

travis:
	pdflatex main.tex

clean:
	latexmk -C

word:
	pandoc main.tex -o main.docx

grammar_check:
	find tex -name '*.tex' ! -name '*Bibliography.tex' ! -name '*config.tex' ! -name '*Contents.tex' -exec java -jar $(LT) -l $(LT_LANG) -d $(LT_IGNORE) {} \;

fetch_grammar_check:
	wget $(LT_DL) -O $(LT_FOLDER).zip
	unzip $(LT_FOLDER).zip -d $(LT_FOLDER)
