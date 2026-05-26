# DickGrowerBot Telegram

A production-ready Telegram game bot built with Python, aiogram, PostgreSQL, Redis, Alembic, Prometheus, and Docker.

## Features

- Daily growth system with cryptographically secure random changes
- Negative growth values and streak tracking
- Per-chat and global leaderboards
- PvP battles with Elo/MMR tracking and critical hits
- Daily event scheduler for "Dick of the Day"
- Inline mode support with shareable game cards
- Admin commands for configuration, reset, export, and import
- CSV / JSON import workflows with validation and logs
- Localization support for English, Russian, and Persian
- Prometheus metrics and health endpoint
- Redis rate limiting and cooldown enforcement
- Async SQLAlchemy repositories and service layer

## Requirements

- Docker
- Docker Compose
- Telegram bot token

## Setup

1. Copy `.env.example` to `.env` and set `BOT_TOKEN`.
2. Start services:

```sh
make compose-up
```

3. Run migrations once:

```sh
make migrate
```

4. The bot listens on Telegram and metrics are available at `http://localhost:8000/metrics`.

## Commands

- `/grow` - grow or shrink once per day
- `/dick`, `/size`, `/stats` - view player stats
- `/top` - leaderboard
- `/fight` - challenge a rival
- `/daily`, `/dotd`, `/winner` - daily event info
- `/admin`, `/config`, `/reset`, `/export`, `/import` - admin operations

## Development

Install dependencies locally:

```sh
make install
```

Run tests:

```sh
make test
```
