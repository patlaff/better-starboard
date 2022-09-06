from discord.ext import commands
from modules.helpers import createLogger, bot
from db import createTables

logger = createLogger('on_ready')

class ReadyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        response = f'We have logged in as {bot.user}'
        logger.info(response)
        print(response)

        # Create SQL Tables & Connect to DB
        createTables()

async def setup(bot):
    await bot.add_cog(ReadyCog(bot))