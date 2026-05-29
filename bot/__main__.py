import asyncio
import os
import subprocess

import discord
from discord.ext import commands
from dotenv import load_dotenv

from . import db as database
from .commands import StarboardConfig
from .starboard import handle_reaction

load_dotenv()


def run_migrations():
    subprocess.run(["alembic", "upgrade", "head"], check=True)


class StarboardBot(commands.Bot):
    def __init__(self, pool):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        intents.guilds = True
        intents.members = False

        super().__init__(command_prefix="|", intents=intents)
        self.pool = pool

    async def setup_hook(self):
        await self.add_cog(StarboardConfig(self, self.pool))

    async def on_ready(self):
        print(f"Logged in as {self.user} ({self.user.id})")

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        await handle_reaction(self.pool, payload, self)


async def main():
    run_migrations()
    pool = await database.create_pool()
    token = os.environ["DISCORD_TOKEN"]
    async with StarboardBot(pool) as bot:
        await bot.start(token)


asyncio.run(main())
