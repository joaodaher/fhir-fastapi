setup:
	@pip install -U pip uv

dependencies:
	@make setup
	@uv sync

update:
	@uv lock --upgrade
	@uv sync

test:
	@make check
	@make lint
	@make unit

check:
	@echo "Checking safety and integrity ..."
	uv run safety check

lint:
	@echo "Checking code style ..."
	uv run ruff check .
	uv run ruff format --check .

style:
	@echo "Applying code style ..."
	uv run ruff check . --fix
	uv run ruff format .

unit:
	@echo "Running unit tests ..."
	ENV=test DEBUG=0 uv run pytest

run-server:
	@uv run uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4

docker-build:
	@docker-compose up --build
