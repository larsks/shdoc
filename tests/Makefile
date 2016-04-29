SHDOC = shdoc

TXTDOCS=$(wildcard *.txt)
HTMLDOCS=$(TXTDOCS:.txt=.html)

%.html: %.txt
	$(SHDOC) -o $@ $<

all: $(HTMLDOCS)

clean:
	rm -f $(HTMLDOCS)
