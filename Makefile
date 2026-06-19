LINT_PATHS = app tests

dev:
	docker-compose up --build

test:
	pytest

lint:
	black --check $(LINT_PATHS)
	isort --check-only $(LINT_PATHS)
	ruff check $(LINT_PATHS)

format:
	black $(LINT_PATHS)
	isort $(LINT_PATHS)
