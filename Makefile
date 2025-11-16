VENV=.venv
PYTHON=$(VENV)/bin/python
PYTHON_NO_CACHE=$(VENV)/bin/python -B
PIP=$(VENV)/bin/pip

# Prevent Python from creating __pycache__ directories
export PYTHONDONTWRITEBYTECODE=1

.PHONY: setup install run module clean clean-cache

setup: ## Create a virtualenv and install dependencies
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	# Prefer requirements-dev.txt if it exists, otherwise fall back to requirements.txt
	if [ -f requirements-dev.txt ]; then \
		$(PIP) install -r requirements-dev.txt; \
	else \
		$(PIP) install -r requirements.txt; \
	fi

install: setup ## Alias for setup
	@echo "Virtualenv created and dependencies installed."

run: ## Run the main script using the venv python (backwards-compatible wrapper)
	mkdir -p data
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src $(PYTHON_NO_CACHE) -m ian_permissions.ian_db_cli

module: ## Run the package as a module (PYTHONPATH=src)
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src $(PYTHON_NO_CACHE) -m ian_permissions

clean-cache: ## Remove __pycache__ directories and .pyc files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Cleaned __pycache__ and .pyc files"

clean: clean-cache ## Remove the virtualenv
	rm -rf $(VENV)
	@echo "Removed $(VENV)"
