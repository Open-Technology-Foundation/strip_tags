# Makefile for strip_tags
# HTML tag stripping utilities (Python + Bash versions)

SHELL := /bin/bash

# Installation paths (override with PREFIX=/usr/local for system install)
PREFIX  ?= $(HOME)/.local
BINDIR  := $(PREFIX)/bin
DATADIR := $(PREFIX)/share/yatti/strip_tags

# GitHub repository
REPO_URL := https://github.com/Open-Technology-Foundation/strip_tags.git

# Files to install
INSTALL_FILES := strip_tags strip_tags.py strip_tags.bash \
                 .symlink .bash_completion requirements.txt \
                 README.md LICENSE

# Executables to symlink (read from .symlink)
SYMLINK_FILES := $(shell cat .symlink 2>/dev/null)

.PHONY: all install install-venv uninstall update link help

all: help

help:
	@echo "strip_tags - HTML tag stripping utilities"
	@echo ""
	@echo "Targets:"
	@echo "  install       Copy files to DATADIR and create symlinks in BINDIR"
	@echo "  install-venv  Create Python venv and install dependencies"
	@echo "  uninstall     Remove symlinks and installed files"
	@echo "  update        Update from GitHub and refresh symlinks"
	@echo "  link          Development: symlink from current directory"
	@echo ""
	@echo "Variables:"
	@echo "  PREFIX=$(PREFIX)"
	@echo "  BINDIR=$(BINDIR)"
	@echo "  DATADIR=$(DATADIR)"
	@echo ""
	@echo "Examples:"
	@echo "  make install                    # User install (~/.local)"
	@echo "  sudo make install PREFIX=/usr/local  # System install"
	@echo "  make link                       # Development symlinks"

install:
	@echo "Installing to $(DATADIR)..."
	@mkdir -p "$(DATADIR)"
	@mkdir -p "$(BINDIR)"
	@for f in $(INSTALL_FILES); do \
		if [[ -f "$$f" ]]; then \
			cp -v "$$f" "$(DATADIR)/"; \
		fi; \
	done
	@echo "Creating symlinks in $(BINDIR)..."
	@for f in $(SYMLINK_FILES); do \
		if [[ -f "$(DATADIR)/$$f" ]]; then \
			ln -sfv "$(DATADIR)/$$f" "$(BINDIR)/$$f"; \
		fi; \
	done
	@echo "Done. Run 'make install-venv' to set up Python environment."

install-venv:
	@if [[ ! -d "$(DATADIR)" ]]; then \
		echo "Error: Run 'make install' first"; \
		exit 1; \
	fi
	@echo "Creating Python venv in $(DATADIR)/.venv..."
	@python3 -m venv "$(DATADIR)/.venv"
	@echo "Installing Python dependencies..."
	@"$(DATADIR)/.venv/bin/pip" install --upgrade pip -q
	@"$(DATADIR)/.venv/bin/pip" install -r "$(DATADIR)/requirements.txt" -q
	@echo "Python venv ready."

uninstall:
	@echo "Removing symlinks from $(BINDIR)..."
	@for f in $(SYMLINK_FILES); do \
		if [[ -L "$(BINDIR)/$$f" ]]; then \
			rm -v "$(BINDIR)/$$f"; \
		fi; \
	done
	@if [[ -d "$(DATADIR)" ]]; then \
		echo "Removing $(DATADIR)..."; \
		rm -rf "$(DATADIR)"; \
	fi
	@echo "Uninstall complete."

update:
	@if [[ -d .git ]]; then \
		echo "Updating from git..."; \
		git pull; \
	elif [[ -d "$(DATADIR)" ]]; then \
		echo "Updating $(DATADIR) from GitHub..."; \
		tmpdir=$$(mktemp -d); \
		git clone --depth 1 "$(REPO_URL)" "$$tmpdir" && \
		for f in $(INSTALL_FILES); do \
			if [[ -f "$$tmpdir/$$f" ]]; then \
				cp -v "$$tmpdir/$$f" "$(DATADIR)/"; \
			fi; \
		done; \
		rm -rf "$$tmpdir"; \
	else \
		echo "Error: No git repo or installation found"; \
		exit 1; \
	fi
	@echo "Refreshing symlinks..."
	@for f in $(SYMLINK_FILES); do \
		if [[ -f "$(DATADIR)/$$f" ]]; then \
			ln -sfv "$(DATADIR)/$$f" "$(BINDIR)/$$f"; \
		elif [[ -f "$$f" ]]; then \
			ln -sfv "$$(pwd)/$$f" "$(BINDIR)/$$f"; \
		fi; \
	done
	@echo "Update complete."

link:
	@echo "Creating development symlinks in $(BINDIR)..."
	@mkdir -p "$(BINDIR)"
	@for f in $(SYMLINK_FILES); do \
		if [[ -f "$$f" ]]; then \
			ln -sfv "$$(pwd)/$$f" "$(BINDIR)/$$f"; \
		fi; \
	done
	@echo "Development symlinks created."
