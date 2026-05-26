FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY pyproject.toml requirements.txt ./
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev \
    && python -m pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt \
    && apt-get purge -y --auto-remove gcc

COPY . .

EXPOSE 8000
CMD ["python", "-m", "app.main"]
