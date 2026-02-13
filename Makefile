.PHONY: install fmt lint type test run up down logs

install:
	poetry install

fmt:
	poetry run ruff format .

lint:
	poetry run ruff check .

type:
	poetry run mypy services libs tests

test:
	poetry run pytest --disable-warnings -v -s

run:
	poetry run uvicorn services.control_api.src.control_api.main:app --reload --port 8000

up:
	docker compose -f deploy/compose/docker-compose.yml up -d

down:
	docker compose -f deploy/compose/docker-compose.yml down -v

logs:
	docker compose -f deploy/compose/docker-compose.yml logs -f
