# Motokvest Bot

A Telegram bot for running motorcycle quest games. Players navigate between checkpoints, solve location-based tasks, and receive real-time inspector feedback — all through Telegram.

[Русская версия](README_RU.md)

## Features

- Three roles: **Player**, **Admin**, **Inspector**
- Admin panel: create game sessions, choose city/date/location, manage attendance before start
- Player flow: receive location → arrive → get task → submit answer → get hints → move to next checkpoint
- Inspector panel: review player answers and approve or reject them
- Game content defined in JSON (locations, tasks, hints, audio, images)
- JSON schema validation when loading new games

## Tech Stack

| Layer | Tools |
|---|---|
| Bot framework | pyTelegramBotAPI 4.29.1 |
| ORM / Database | Peewee 3.18.2 + SQLite |
| Config | python-dotenv |
| Validation | jsonschema |
| Tests | pytest 9.0.3 — 119 tests |

## Architecture

Three design patterns structure the codebase:

**State Machine** (`states/`)  
Every user has a `UserState` value stored in the database. When a message arrives, `UserStatesService` reads the state, instantiates the matching state object via `StateFactory`, and delegates to its `handle()` method. Each state is responsible for its own logic and transitions — no nested `if/else` chains across handlers.

**Dependency Injection Container** (`core/container.py`)  
A single `Container` class wires all dependencies (bot instance, repositories, services) at startup. Nothing is instantiated at import time. `get_container()` returns the singleton. This makes the dependency graph explicit and testable.

**Repository Pattern** (`database/repositories/`)  
Nine repositories wrap Peewee models and expose domain-specific methods. Services call repository methods and never touch ORM queries directly. In tests, repositories run against an in-memory SQLite database — no mocks needed for data layer tests.

Other patterns in use: decorator-based cross-cutting concerns (`with_context`, `error_guard`, `log_exceptions`), DTO objects for passing structured data between layers, compare-and-swap in `UserRepository` to prevent race conditions in multi-threaded pyTelegramBotAPI polling.

## Project Structure

```
motokvest_bot/
├── bot/                    # Entry point (main.py)
├── cli/                    # CLI scripts: load game, set admin, recover user
├── config_data/            # Env config + JSON schema for game files
├── core/
│   ├── container.py        # DI container
│   ├── dto/                # Data transfer objects
│   ├── enums/              # UserState, UserRole, SessionState, ...
│   └── utils/              # Input validation helpers
├── database/
│   ├── models/             # Peewee models (User, GameSession, PointProgress, ...)
│   └── repositories/       # 9 repositories (BaseRepository + domain-specific)
├── decorators/             # with_context, error_guard, log_exceptions
├── games_data/             # Game content in JSON + media files
├── handlers/               # Telegram message and callback routers
├── presenters/             # Text and keyboard builders
├── services/               # Business logic (AdminHandler, InspectorHandler, UIService, ...)
├── states/                 # State machine: BaseUserState, StateFactory, all state classes
└── tests/                  # pytest suite: 119 tests across 9 test files
```

## Setup

**1. Clone and install dependencies**

```bash
git clone https://github.com/pybyOx/motoquest_bot.git
cd motoquest_bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Configure environment**

Copy `.env.template` to `.env` and fill in the values:

```
BOT_TOKEN=your_telegram_bot_token
MAIN_ADMIN_ID=telegram_user_id
ADMIN_IDS=id1,id2         # comma-separated, can be empty
INSPECTOR_ID=telegram_user_id
```

**3. Load game data**

```bash
python -m cli.create_game games_data/way_of_the_dragon/game_dragon.json
```

See `games_data/README.md` for the JSON format and how to create your own game.

**4. Set admin role**

```bash
python -m cli.set_admin <telegram_user_id>
```

**5. Run the bot**

```bash
python -m bot.main
```

## Running Tests

```bash
pytest
```

All tests use an in-memory SQLite database and run without any external services.

## Roles

| Role | How to get it | Capabilities |
|---|---|---|
| Player | `/start` → registration | Navigate checkpoints, submit answers, request hints |
| Admin | Set via CLI | Create/manage game sessions, attendance check, start game |
| Inspector | Set via `INSPECTOR_ID` in `.env` | Review and approve player answers |
