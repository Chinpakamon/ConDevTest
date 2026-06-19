dev:
	docker-compose up --build

test:
	pytest

lint:
	black --check app tests
	isort --check-only app tests
	ruff check app tests
