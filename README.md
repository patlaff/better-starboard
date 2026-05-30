# better-starboard

A Discord bot that surfaces the most-reacted-to messages in your community. When a message accumulates enough reactions from other members, the bot automatically reposts it to a designated starboard channel — acting as a community-curated highlights feed.

**Key differentiator:** any reaction counts, not just a specific emoji. Total reaction volume across all emoji types determines whether a message qualifies.

---

## Installation

[Install Using This Link](https://discord.com/api/oauth2/authorize?client_id=1008147831443427379&permissions=8&scope=bot)

Note that the bot currently requires administrator rights. I will pull in these permissions in a future release.

---

## Features

- Posts messages to a starboard channel once they hit a configurable reaction threshold
- Counts all emoji types — no single "star" emoji required
- Updates the starboard embed live as more reactions accumulate
- Per-server configuration: channel, threshold, ignored channels, ignored emoji
- Duplicate-proof: a message is never posted to the starboard more than once
- Multi-server: one bot instance serves many Discord servers independently

---

## Requirements

- Docker and Docker Compose
- A Discord bot token ([create one here](https://discord.com/developers/applications))
- A pre-existing channel in your server to use as the starboard

### Discord bot settings

In the [Discord Developer Portal](https://discord.com/developers/applications), under your bot's settings:

- **Privileged Gateway Intents:** enable **Message Content Intent**
- **Bot Permissions:** `Read Messages`, `Send Messages`, `Embed Links`, `Read Message History`

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/yourname/better-starboard.git
cd better-starboard
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set your bot token:

```
DISCORD_TOKEN=your_bot_token_here
DATABASE_URL=postgresql://starboard:starboard@db:5432/starboard
```

The `DATABASE_URL` default works with the included `docker-compose.yml` as-is. Only change it if you're pointing at an external database.

### 3. Start the bot

```bash
docker compose up --build
```

The bot runs database migrations automatically on startup, then connects to Discord. You should see:

```
Logged in as YourBot#1234 (123456789)
```

### 4. Configure your server

In your Discord server, run:

```
|set starboard
```

Replace `starboard` with the name of whatever channel you want pinned messages to appear in. This channel must already exist. That's it — the bot is now active with a default threshold of 5 reactions.

---

## Commands

All commands require **Manage Channels** and **Manage Messages** permissions.

### Initial setup

| Command | Description |
|---------|-------------|
| `\|set #channel` | Set the starboard channel. Required before anything else works. Sets the default threshold to 5 on first use. Pass a channel mention or ID. |

### Tuning

| Command | Description |
|---------|-------------|
| `\|threshold <number>` | Change the minimum total reactions needed before a message is pinned. Raise it to make the starboard more exclusive; lower it to be more permissive. |

### Channel exceptions

| Command | Description |
|---------|-------------|
| `\|ignore_channel #channel` | Reactions in this channel will never trigger starboard posting. Useful for spoiler channels, bot-command channels, etc. Pass a channel mention or ID. |
| `\|add_channel #channel` | Remove a channel from the ignore list, re-enabling starboard eligibility. Pass a channel mention or ID. |

### Reaction exceptions

| Command | Description |
|---------|-------------|
| `\|ignore_reaction <emoji>` | This emoji will not count toward the reaction threshold. Useful for downvote emoji or sarcastic reactions you don't want rewarding content. |
| `\|add_reaction <emoji>` | Remove an emoji from the ignore list, re-enabling it as a qualifying reaction. |

### Status

| Command | Description |
|---------|-------------|
| `\|status` | Display the server's current configuration: starboard channel, threshold, ignored channels, and ignored reactions. |

---

## How pinning works

Every time any user adds a reaction to any message, the bot evaluates it:

1. **Channel filter** — if the message's channel is on the ignore list, stop.
2. **Reaction filter** — if the specific emoji added is on the ignore list, stop.
3. **Config check** — if this server hasn't been set up yet, stop.
4. **Count reactions** — sum all reactions across all emoji types, excluding ignored emoji.
5. **Already pinned?**
   - Yes → update the existing starboard embed with the new count.
   - No, and count ≥ threshold → post a new embed to the starboard channel and record the pin.

Reaction removals are not currently handled. A message that reaches the threshold stays pinned even if reactions are later removed.

---

## Project structure

```
better-starboard/
├── bot/
│   ├── __init__.py
│   ├── __main__.py      # Entry point: migrations, DB pool, bot lifecycle
│   ├── commands.py      # Prefix commands (|set, |threshold, etc.)
│   ├── db.py            # All database queries via asyncpg
│   └── starboard.py     # Core reaction logic: filter → count → post/update
├── migrations/
│   ├── env.py           # Alembic environment config
│   ├── script.py.mako   # Migration template
│   └── versions/
│       └── 0001_initial.py  # Initial schema
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Data model

All state is scoped per Discord server (guild).

| Table | Description |
|-------|-------------|
| `server_config` | Starboard channel ID and reaction threshold per server |
| `pins` | Maps original messages to their starboard copies; prevents duplicates |
| `ignored_channels` | Channels excluded from starboard consideration |
| `ignored_reactions` | Emoji excluded from the reaction count |

---

## Development

### Running locally without Docker

You'll need Python 3.12+ and a running PostgreSQL instance.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export DISCORD_TOKEN=your_token
export DATABASE_URL=postgresql://user:pass@localhost:5432/starboard

alembic upgrade head
python -m bot
```

### Adding a database migration

```bash
alembic revision -m "describe your change"
# Edit the generated file in migrations/versions/
alembic upgrade head
```

---

## Known limitations

- **Reaction removals are not handled.** Removing reactions does not un-pin a message or update its count downward.
- **No retroactive scanning.** Messages that accumulated reactions before the bot was added, or before the threshold was lowered, will not be retroactively pinned.
- **The starboard channel must exist before running `|set`.** The bot validates this and rejects channel names that don't match an existing text channel.
- **Custom emoji from other servers** are referenced by their numeric ID rather than name when added to the ignore list.

---

## License

MIT
