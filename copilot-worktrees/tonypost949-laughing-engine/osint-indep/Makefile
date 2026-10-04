# OSINT Independent Platform - Makefile
# Build automation and common tasks

.PHONY: help install test test-cov lint format type-check clean build docker-build docker-up docker-down docker-logs db-init db-migrate db-reset backup verify sync sync-gdrive sync-local assets-download health-check

# Default target
help:
	@echo "OSINT Independent Platform - Build Commands"
	@echo ""
	@echo "Development:"
	@echo "  install         Install Python dependencies"
	@echo "  test            Run tests"
	@echo "  test-cov        Run tests with coverage"
	@echo "  lint            Run linting (ruff, black, isort)"
	@echo "  format          Format code (black, isort)"
	@echo "  type-check      Run mypy type checking"
	@echo ""
	@echo "Database:"
	@echo "  db-init         Initialize database"
	@echo "  db-migrate      Run migrations"
	@echo "  db-reset        Reset database (DANGEROUS)"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build    Build Docker images"
	@echo "  docker-up       Start services"
	@echo "  docker-down     Stop services"
	@echo "  docker-logs     View logs"
	@echo ""
	@echo "Backup & Sync:"
	@echo "  backup          Create full backup"
	@echo "  verify          Verify all backups"
	@echo "  sync            Sync to all backup tiers"
	@echo "  sync-gdrive     Sync to Google Drive"
	@echo "  sync-local      Sync to local backup"
	@echo ""
	@echo "Assets:"
	@echo "  assets-download Download vendor assets"
	@echo "  assets-verify   Verify asset integrity"
	@echo ""
	@echo "Health:"
	@echo "  health-check    Run full health check"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean           Remove build artifacts"

# Python environment
VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

# Install dependencies
install: $(VENV)/bin/activate
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e .[dev]

$(VENV)/bin/activate:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

# Testing
test:
	$(PYTHON) -m pytest tests/ -v

test-cov:
	$(PYTHON) -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Linting
lint:
	$(VENV)/bin/ruff check src/ tests/
	$(VENV)/bin/black --check src/ tests/
	$(VENV)/bin/isort --check-only src/ tests/

format:
	$(VENV)/bin/black src/ tests/
	$(VENV)/bin/isort src/ tests/

type-check:
	$(VENV)/bin/mypy src/

# Database
db-init:
	$(PYTHON) -m src.core.database init

db-migrate:
	$(PYTHON) -m alembic upgrade head

db-reset:
	@echo "WARNING: This will destroy all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(PYTHON) -m src.core.database reset; \
	fi

# Docker
docker-build:
	docker-compose build --parallel

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Backup & Sync
backup:
	./scripts/create-cold-backup.sh

verify:
	./scripts/verify-backups.sh

sync:
	./scripts/sync-all.sh

sync-gdrive:
	./scripts/sync-to-gdrive.sh

sync-local:
	powershell -ExecutionPolicy Bypass -File scripts/sync-to-local.ps1

# Assets
assets-download:
	./scripts/download-assets.sh

assets-verify:
	./scripts/verify-assets.sh

# Health
health-check:
	./scripts/health-check.sh

# Cleanup
clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	docker system prune -f

# Pre-commit
pre-commit:
	pre-commit run --all-files

# CI simulation
ci: lint type-check test
	@echo "All CI checks passed!"

# Quick development cycle
dev: install db-init
	@echo "Development environment ready!"
	@echo "Run 'make docker-up' to start services"