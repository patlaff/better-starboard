import asyncpg
import os


async def create_pool() -> asyncpg.Pool:
    return await asyncpg.create_pool(os.environ["DATABASE_URL"])


# ---------- server_config ----------

async def get_config(pool: asyncpg.Pool, guild_id: int):
    return await pool.fetchrow(
        "SELECT * FROM server_config WHERE guild_id = $1", guild_id
    )


async def set_starboard_channel(pool: asyncpg.Pool, guild_id: int, channel_id: int):
    await pool.execute(
        """
        INSERT INTO server_config (guild_id, starboard_channel_id, threshold)
        VALUES ($1, $2, 5)
        ON CONFLICT (guild_id) DO UPDATE SET starboard_channel_id = $2
        """,
        guild_id,
        channel_id,
    )


async def set_threshold(pool: asyncpg.Pool, guild_id: int, threshold: int):
    await pool.execute(
        "UPDATE server_config SET threshold = $2 WHERE guild_id = $1",
        guild_id,
        threshold,
    )


# ---------- pins ----------

async def get_pin(pool: asyncpg.Pool, guild_id: int, message_id: int):
    return await pool.fetchrow(
        "SELECT * FROM pins WHERE guild_id = $1 AND original_message_id = $2",
        guild_id,
        message_id,
    )


async def create_pin(
    pool: asyncpg.Pool,
    guild_id: int,
    original_message_id: int,
    original_channel_id: int,
    starboard_message_id: int,
):
    await pool.execute(
        """
        INSERT INTO pins (guild_id, original_message_id, original_channel_id, starboard_message_id)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT DO NOTHING
        """,
        guild_id,
        original_message_id,
        original_channel_id,
        starboard_message_id,
    )


# ---------- ignored channels ----------

async def get_ignored_channels(pool: asyncpg.Pool, guild_id: int) -> list[int]:
    rows = await pool.fetch(
        "SELECT channel_id FROM ignored_channels WHERE guild_id = $1", guild_id
    )
    return [r["channel_id"] for r in rows]


async def add_ignored_channel(pool: asyncpg.Pool, guild_id: int, channel_id: int):
    await pool.execute(
        "INSERT INTO ignored_channels (guild_id, channel_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
        guild_id,
        channel_id,
    )


async def remove_ignored_channel(pool: asyncpg.Pool, guild_id: int, channel_id: int):
    await pool.execute(
        "DELETE FROM ignored_channels WHERE guild_id = $1 AND channel_id = $2",
        guild_id,
        channel_id,
    )


# ---------- ignored reactions ----------

async def get_ignored_reactions(pool: asyncpg.Pool, guild_id: int) -> list[str]:
    rows = await pool.fetch(
        "SELECT emoji FROM ignored_reactions WHERE guild_id = $1", guild_id
    )
    return [r["emoji"] for r in rows]


async def add_ignored_reaction(pool: asyncpg.Pool, guild_id: int, emoji: str):
    await pool.execute(
        "INSERT INTO ignored_reactions (guild_id, emoji) VALUES ($1, $2) ON CONFLICT DO NOTHING",
        guild_id,
        emoji,
    )


async def remove_ignored_reaction(pool: asyncpg.Pool, guild_id: int, emoji: str):
    await pool.execute(
        "DELETE FROM ignored_reactions WHERE guild_id = $1 AND emoji = $2",
        guild_id,
        emoji,
    )
