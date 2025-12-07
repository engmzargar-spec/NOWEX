# Makefile

.PHONY: dev build test clean migrate seed

dev:
	@echo "Starting all services in development mode..."
	docker-compose up -d postgres redis
	@echo "Services started. Run backend and frontend manually."

build:
	@echo "Building Docker images..."
	docker build -t nowex-backend -f backend/Dockerfile .
	docker build -t nowex-frontend -f frontend/Dockerfile .

test:
	@echo "Running tests..."
	cd backend && python -m pytest

clean:
	@echo "Cleaning up..."
	docker-compose down
	docker system prune -f

migrate:
	@echo "Running database migrations..."
	cd backend && alembic upgrade head

seed:
	@echo "Seeding database with initial data..."
	cd backend && python scripts/seed_data.py

db-shell:
	docker exec -it nowex_postgres psql -U nowex_user -d nowex_development