# Makefile - Install strip_tags
# BCS1212 compliant

PREFIX  ?= /usr/local
BINDIR  ?= $(PREFIX)/bin
COMPDIR ?= /etc/bash_completion.d
DESTDIR ?=

.PHONY: all install uninstall check help

all: help

install:
	install -d $(DESTDIR)$(BINDIR)
	install -m 755 strip_tags $(DESTDIR)$(BINDIR)/strip_tags
	install -m 755 strip_tags.bash $(DESTDIR)$(BINDIR)/strip_tags.bash
	install -m 755 strip_tags.py $(DESTDIR)$(BINDIR)/strip_tags.py
	ln -sf strip_tags.bash $(DESTDIR)$(BINDIR)/strip-tags
	@if [ -d $(DESTDIR)$(COMPDIR) ]; then \
	  install -m 644 .bash_completion $(DESTDIR)$(COMPDIR)/strip_tags; \
	fi
	@if [ -z "$(DESTDIR)" ]; then $(MAKE) --no-print-directory check; fi

uninstall:
	rm -f $(DESTDIR)$(BINDIR)/strip_tags
	rm -f $(DESTDIR)$(BINDIR)/strip_tags.bash
	rm -f $(DESTDIR)$(BINDIR)/strip_tags.py
	rm -f $(DESTDIR)$(BINDIR)/strip-tags
	rm -f $(DESTDIR)$(COMPDIR)/strip_tags

check:
	@command -v strip_tags >/dev/null 2>&1 \
	  && echo 'strip_tags: OK' \
	  || echo 'strip_tags: NOT FOUND (check PATH)'

help:
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@echo '  install     Install to $(PREFIX)'
	@echo '  uninstall   Remove installed files'
	@echo '  check       Verify installation'
	@echo '  help        Show this message'
	@echo ''
	@echo 'Install from GitHub:'
	@echo '  git clone https://github.com/Open-Technology-Foundation/strip_tags.git'
	@echo '  cd strip_tags && sudo make install'
