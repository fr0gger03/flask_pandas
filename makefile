.PHONY: help dev dev-down dev-rebuild prod-up prod-down prod-rebuild dhi-up dhi-down test test-ci clean

help:
	@echo "Flask Pandas Project - Makefile Commands"
	@echo ""
	@echo "Development:"
	@echo "  make dev              - Start local development environment"
	@echo "  make dev-down         - Stop local development environment"
	@echo "  make dev-rebuild      - Rebuild and restart local development"
	@echo ""
	@echo "Production:"
	@echo "  make prod-up          - Start production environment"
	@echo "  make prod-down        - Stop production environment"
	@echo "  make prod-rebuild     - Rebuild and restart production"
	@echo "  make prod-logs        - View production logs"
	@echo ""
	@echo "DHI:"
	@echo "  make dhi-up           - Start DHI environment"
	@echo "  make dhi-down         - Stop DHI environment"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run test suite"
	@echo "  make test-ci          - Run tests with 1Password (CI mode)"
	@echo "  make test-coverage    - Run tests with coverage report"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean            - Remove containers and volumes"

dev:
	./deploy.sh local build --no-cache
	./deploy.sh local up

dev-down:
	./deploy.sh local down

dev-rebuild:
	./deploy.sh local build --no-cache
	./deploy.sh local up --force-recreate

prod-up:
	./deploy.sh production build --no-cache
	./deploy.sh production up -d

prod-down:
	./deploy.sh production down

prod-rebuild:
	./deploy.sh production build --no-cache
	./deploy.sh production up -d --force-recreate

prod-logs:
	./deploy.sh production logs -f

dhi-up:
	./deploy.sh dhi build --no-cache
	./deploy.sh dhi up -d

dhi-down:
	./deploy.sh dhi down

test:
	./scripts/test.sh

test-ci:
	./scripts/test-ci.sh

test-coverage:
	./scripts/test.sh --cov=parser --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

clean:
	docker compose down -v
	rm -rf htmlcov .pytest_cache .coverage