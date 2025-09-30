.PHONY: help dev build test clean seed

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

dev: ## Start development environment
	docker-compose -f infra/docker-compose.yml up --build

build: ## Build all services
	docker-compose -f infra/docker-compose.yml build

test: ## Run tests
	docker-compose -f infra/docker-compose.yml run --rm api pytest
	docker-compose -f infra/docker-compose.yml run --rm web npm test

clean: ## Clean up containers and volumes
	docker-compose -f infra/docker-compose.yml down -v
	docker system prune -f

seed: ## Seed database with initial data
	docker-compose -f infra/docker-compose.yml run --rm api python -m scripts.seed

logs: ## Show logs
	docker-compose -f infra/docker-compose.yml logs -f

api-shell: ## Open API container shell
	docker-compose -f infra/docker-compose.yml exec api bash

db-shell: ## Open database shell
	docker-compose -f infra/docker-compose.yml exec db psql -U mousealerts -d mousealerts

migrate: ## Run database migrations
	docker-compose -f infra/docker-compose.yml run --rm api alembic upgrade head

migrate-create: ## Create new migration
	docker-compose -f infra/docker-compose.yml run --rm api alembic revision --autogenerate -m "$(name)"
