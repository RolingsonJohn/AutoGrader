.PHONY: help install dev test lint format clean build run docker-build docker-run

help:
	@echo "AutoGrader Makefile Commands"
	@echo "============================="
	@echo "make install       - Install production dependencies"
	@echo "make dev           - Install development dependencies"
	@echo "make test          - Run test suite with coverage"
	@echo "make lint          - Run linters (flake8, black, mypy)"
	@echo "make format        - Format code with black and isort"
	@echo "make clean         - Clean up cache and build artifacts"
	@echo "make build         - Build FastAPI and Django applications"
	@echo "make run           - Run FastAPI application"
	@echo "make django-run    - Run Django development server"
	@echo "make docker-build  - Build Docker image"
	@echo "make docker-run    - Run Docker container"

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements.txt
	pip install -e ".[dev]"
	pre-commit install

test:
	cd fastapi_app && pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing

test-fast:
	cd fastapi_app && pytest tests/ -v --tb=short

lint:
	flake8 fastapi_app --count --statistics
	black --check fastapi_app
	mypy fastapi_app --ignore-missing-imports || true

format:
	black fastapi_app
	isort fastapi_app

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .coverage -delete
	find . -type d -name htmlcov -exec rm -rf {} +
	rm -rf build/ dist/ *.egg-info/

build: clean test lint
	@echo "Build complete!"

run:
	cd fastapi_app && uvicorn main:app --reload --host 0.0.0.0 --port 8000

django-run:
	cd backend/AutoGrader && python manage.py runserver

docker-build:
	docker build -f Dockerfile -t autograder:latest .

docker-run: docker-build
	docker run -p 8000:8000 -p 8001:8001 --env-file .env autograder:latest

docker-compose-up:
	docker-compose up --build

docker-compose-down:
	docker-compose down

.DEFAULT_GOAL := help
