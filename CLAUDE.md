# CLAUDE.md — AI Assistant Guide for better-starboard

## Project Overview

**better-starboard** is a Discord bot that automatically pins popular messages to a designated "starboard" channel. Unlike traditional starboard bots, it tracks *any* reaction (not just a specific emoji) and pins messages when the total reaction count crosses a configurable threshold. It is written in Python using discord.py and deployed via Docker.

---

## Repository Structure

```
better-starboard/
├── src/
│   ├── better-starboard.py        # Entry point; loads cogs and starts bot
│   ├── requirements.txt           # Python dependencies (discord.py, python-dotenv)
│   ├── cogs/                      # Discord command modules (one per feature area)
│   │   ├── config.py              # |set and |threshold commands
│   │   ├── general.py             # |status command
│   │   ├── channel_management.py  # |ignore_channel and |add_channel commands
│   │   ├── reaction_management.py # |ignore_reaction and |add_reaction commands
│   │   └── events.py              # Discord event handlers (core starboard logic)
│   └── helpers/
│       ├── __init__.py            # Empty package file
│       ├── helpers.py             # Shared utilities (bot, logger, DB, embed creation)
│       ├── db.py                  # SQLite schema creation (idempotent)
│       └── vars.py                # Global constants (bot name, default threshold)
├── Dockerfile                     # Docker image definition (python:3.10-buster)
├── .github/
│   └── workflows/
│       ├── deploy.yaml            # CI/CD trigger (push to dev/main)
│       └── deploy-reusable.yaml   # Reusable deploy workflow (SSH + Docker)
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── privacy_policy.md
└── terms_of_service.md
```

---

## Technology Stack

| Component   | Choice                         |
|-------------|--------------------------------|
| Language    | Python 3.10+                   |
| Framework   | discord.py 2.0.0               |
| Database    | SQLite3 (direct, no ORM)       |
| Config      | python-dotenv (`.env` file)    |
| Deployment  | Docker + GitHub Actions (SSH)  |
| Logging     | Python `logging` module        |

---

## Running the Bot Locally

1. **Install dependencies:**
   ```bash
   pip install -r src/requirements.txt
   ```

2. **Create a `.env` file** in the project root:
   ```
   BS_TOKEN=your_discord_bot_token_here
   ```

3. **Run the bot:**
   ```bash
   cd src
   python better-starboard.py
   ```

The bot expects `/bs/db/` and `/bs/logs/` directories for the database and log files. When running locally outside Docker, these will be created automatically by `createDir()` in `helpers.py`.

---

## Running with Docker

```bash
docker build -t better-starboard .
docker run -d \
  --name better-starboard \
  -v bsdb:/bs/db \
  -v bslogs:/bs/logs \
  --env-file .env \
  better-starboard
```

---

## Environment Variables

| Variable   | Required | Description                       |
|------------|----------|-----------------------------------|
| `BS_TOKEN` | Yes      | Discord bot token from .env file  |

---

## Database Schema

SQLite database at `/bs/db/bs.db`. Tables are created idempotently on bot startup via `createTables()` in `src/helpers/db.py`.

```sql
PINS
  sb_message_id  INTEGER PRIMARY KEY   -- Starboard message ID (in starboard channel)
  guild_id       INTEGER               -- Discord server ID
  channel_id     INTEGER               -- Original message's channel ID
  message_id     INTEGER               -- Original message ID

CONFIGS
  guild_id                  INTEGER PRIMARY KEY  -- Discord server ID
  sb_channel_name           TEXT                 -- Starboard channel name
  reaction_count_threshold  INTEGER              -- Pin threshold (default: 5)

CHANNEL_EXCEPTIONS
  id           TEXT PRIMARY KEY   -- Composite: str(guild_id) + channel_name
  guild_id     INTEGER
  channel_name TEXT

REACTION_EXCEPTIONS
  id        TEXT PRIMARY KEY   -- Composite: str(guild_id) + reaction
  guild_id  INTEGER
  reaction  TEXT
```

**Important:** There is a single shared global SQLite connection created at startup (`createDbConn()` in `helpers.py`). No connection pooling. No ORM. Use raw SQL with the `sqlite3` module.

---

## Bot Commands

All commands use the `|` prefix (hardcoded, not configurable).
All commands require the **"Manage Channels"** and **"Manage Messages"** Discord permissions.

| Command                       | Description                                       |
|-------------------------------|---------------------------------------------------|
| `\|set <channel_name>`         | Set the starboard output channel                  |
| `\|threshold <int>`            | Set the reaction threshold (default: 5)           |
| `\|status`                     | Show current server configuration                 |
| `\|ignore_channel <name>`      | Add a channel to the blacklist                    |
| `\|add_channel <name>`         | Remove a channel from the blacklist               |
| `\|ignore_reaction <emoji>`    | Add a reaction/emoji to the ignore list           |
| `\|add_reaction <emoji>`       | Remove a reaction/emoji from the ignore list      |

---

## Core Logic: How Pinning Works

The main logic lives in `src/cogs/events.py` → `on_raw_reaction_add`:

1. Check if the reacted channel is in `CHANNEL_EXCEPTIONS` → skip if so.
2. Check if the reaction emoji is in `REACTION_EXCEPTIONS` → skip if so.
3. Look up the server config in `CONFIGS` → skip if not configured.
4. Fetch the original message and count total reactions.
5. If a starboard entry already exists in `PINS`, **edit** the existing embed with the updated reaction count.
6. If total reactions meet or exceed the threshold and no pin exists yet, **post** a new embed to the starboard channel and insert into `PINS`.

---

## Code Architecture Conventions

### Cog Pattern
Each feature area is a separate cog in `src/cogs/`. Cogs are auto-loaded dynamically by the entry point:
```python
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        await bot.load_extension(f'cogs.{filename[:-3]}')
```

When adding a new command group, create a new cog file in `src/cogs/`.

### Shared Utilities
All shared objects (bot instance, logger instances, DB connection) are initialized in `src/helpers/helpers.py` and imported into cogs. Do not create new bot instances or DB connections in cogs.

### Logging
Each cog/module has its own named logger created via `createLogger(name)`. Log files go to `/bs/logs/<name>.log`. Use `INFO` level for normal operations, `ERROR` for failures.

### Permission Checks
All commands that modify server configuration must include:
```python
@commands.has_permissions(manage_channels=True, manage_messages=True)
```

### Duplicate Handling
Duplicate inserts into `CHANNEL_EXCEPTIONS` and `REACTION_EXCEPTIONS` are handled by catching `sqlite3.IntegrityError` (not by pre-checking). Follow this same pattern for new tables with unique constraints.

### Embed Formatting
Starboard embeds are created by `createEmbed()` in `helpers.py`. The embed includes the original message content, author, and reaction count. Always use this helper for consistency.

---

## CI/CD & Deployment

**Triggers:** Push to `main` (prod) or `dev` branch with changes in `src/`, `Dockerfile`, or `.github/workflows/`.

**Deployment process** (via `deploy-reusable.yaml`):
1. Inject `BS_TOKEN` into `.env`
2. SSH to deployment server
3. SCP project files to server
4. Build Docker image on server
5. Stop and remove old container, start new one

**Secrets required in GitHub:**
- `BS_TOKEN` — Discord bot token
- `HOST`, `USERNAME`, `PASSWORD`, `PORT` — SSH credentials

**Volume names:**
- Prod: `bsdb` / `bslogs`
- Dev: `bsdb-dev` / `bslogs-dev`

---

## Key Files to Understand First

When modifying this codebase, read these files in order:

1. `src/helpers/vars.py` — Global constants
2. `src/helpers/helpers.py` — All shared setup functions
3. `src/helpers/db.py` — Database schema
4. `src/cogs/events.py` — Core starboard logic
5. The specific cog you need to modify

---

## What This Project Does NOT Have

- No test suite (no pytest, unittest, or test files)
- No ORM or migration framework (raw SQLite SQL only)
- No connection pooling (single shared connection)
- No configurable bot prefix (hardcoded to `|`)
- No metrics or monitoring integration
- No async database driver (synchronous `sqlite3` calls in async handlers)
