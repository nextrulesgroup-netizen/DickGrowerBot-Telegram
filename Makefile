install:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

compose-up:
	docker compose up --build

compose-down:
	docker compose down

migrate:
	docker compose run --rm bot alembic upgrade head

test:
	pytest
