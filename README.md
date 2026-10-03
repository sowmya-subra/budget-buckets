# budget-buckets

Daily transaction bucketing with a push digest and budget dashboard.

## Prerequisites
- [uv](https://docs.astral.sh/uv/)
- Docker with Compose

## Setup
    uv sync
    uv run pre-commit install
    cp .env.example .env   # then fill in values
    docker compose up -d

## Common commands
    uv run pytest          # tests
    uv run ruff check      # lint
    docker compose down    # stop Postgres
