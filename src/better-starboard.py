import os
import asyncio
from helpers import bot
from dotenv import load_dotenv

async def load_extensions():

    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f"cogs.{filename[:-3]}")


async def main():
    # Load token
    load_dotenv()

    #async with bot:
    await load_extensions()
    await bot.start(os.getenv('BS_TOKEN'))
        

# Run bot
asyncio.run(main())