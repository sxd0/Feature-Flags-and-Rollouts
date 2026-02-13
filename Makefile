.PHONY: install fmt lint type test pretty pretty-validate run up down logs db alembic-rev alembic-up run-control run-data

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

pretty:
	poetry run ruff format .
	poetry run ruff check .
	poetry run mypy services libs tests

pretty-validate:
	poetry run ruff format .
	poetry run ruff check --fix
	poetry run mypy services libs tests

run:
	poetry run uvicorn services.control_api.src.control_api.main:app --reload --port 8000

up:
	docker-compose -f deploy/compose/docker-compose.yml up -d

down:
	docker-compose -f deploy/compose/docker-compose.yml down -v

logs:
	docker-compose -f deploy/compose/docker-compose.yml logs -f

db:
	docker-compose -f deploy/compose/docker-compose.yml exec postgres psql -U postgres -d ff

alembic-rev:
	PYTHONPATH=. poetry run alembic revision --autogenerate -m "$(m)"

alembic-up:
	PYTHONPATH=. poetry run alembic upgrade head

run-control:
	poetry run uvicorn services.control_api.src.control_api.main:app --reload --port 8000

run-data:
	poetry run uvicorn services.data_plane.src.data_plane.main:app --reload --port 8001
