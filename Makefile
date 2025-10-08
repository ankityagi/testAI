PYTHON := python3
VENV ?= testai-env
PIP := $(VENV)/bin/pip
PYTHON_BIN := $(VENV)/bin/python

.PHONY: install install-dev dev lint test format

$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip

install: $(VENV)/bin/activate
	$(PIP) install -r requirements.txt

install-dev: $(VENV)/bin/activate
	$(PIP) install -r requirements-dev.txt

dev:
	$(PYTHON_BIN) -m uvicorn studybuddy.backend.app:app --reload --port 8000

lint:
	$(PYTHON_BIN) -m compileall studybuddy

format:
	$(PYTHON_BIN) -m pip install ruff && $(PYTHON_BIN) -m ruff format studybuddy

test:
	$(PYTHON_BIN) -m pytest
