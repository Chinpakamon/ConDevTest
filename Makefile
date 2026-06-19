dev:
	docker-compose up --build

test:
	pytest

lint:
	ruff check app tests
