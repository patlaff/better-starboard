import os
import asyncio
from modules.helpers import bot
from dotenv import load_dotenv

async def load_extensions():

    # Load Events
    await bot.load_extension("modules.on_ready")
    await bot.load_extension("modules.on_reaction")
    
    # Load Commands
    await bot.load_extension("modules.set")
    await bot.load_extension("modules.threshold")
    await bot.load_extension("modules.ignore_channel")
    await bot.load_extension("modules.ignore_reaction")
    await bot.load_extension("modules.status")


async def main():
    # Load token
    load_dotenv()

    async with bot:
        await load_extensions()
        await bot.start(os.getenv('BS_TOKEN'))

# Run bot
asyncio.run(main())