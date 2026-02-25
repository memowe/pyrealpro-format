SHELL := /bin/bash

PY ?= python3
VENV ?= env

VENV_PY := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip
DEPS_SENTINEL := $(VENV)/.deps-installed
PYPROJECT := pyproject.toml
SOURCE_FOLDERS := pyrealpro_format test utils

IREAL_PRO_PLAYLISTS := https://www.irealpro.com/main-playlists/
IREAL_PRO_PLAYLISTS_DIR := playlists

.PHONY: all
all: check test

.PHONY: check
check: install_deps
	$(VENV_PY) -m compileall $(SOURCE_FOLDERS)
	$(VENV_PY) -m mypy --strict $(SOURCE_FOLDERS)
	. $(VENV)/bin/activate && pyright --level error $(SOURCE_FOLDERS)
	$(VENV_PY) -m black --check $(SOURCE_FOLDERS)

.PHONY: test
test: install_deps $(IREAL_PRO_PLAYLISTS_DIR)
	$(VENV_PY) -m pytest -v

$(VENV):
	$(PY) -m venv $(VENV)
	$(VENV_PIP) install --upgrade pip setuptools

install_deps: $(DEPS_SENTINEL)

$(DEPS_SENTINEL): $(PYPROJECT) | $(VENV)
	$(VENV_PIP) install -e .[dev]
	touch $@

.PHONY: download_playlists
download_playlists: $(IREAL_PRO_PLAYLISTS_DIR)

$(IREAL_PRO_PLAYLISTS_DIR): install_deps
	mkdir -p $@
	$(VENV_PY) utils/download_playlists.py \
		--url $(IREAL_PRO_PLAYLISTS) \
		--output $(IREAL_PRO_PLAYLISTS_DIR)

.PHONY: clean
clean:
	rm -rf $(VENV)
	rm -rf $(IREAL_PRO_PLAYLISTS_DIR)
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache
