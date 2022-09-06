import discord
from discord.ext import commands
from modules import vars
from modules.helpers import createLogger, conn, bot
import sqlite3 as sql

logger = createLogger('ignore_channel')

class IgChannelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help=f"Use this command to set channel exceptions for {vars.bot_name}.",
        brief="Use |ignore <channel_name> to add a channel exception."
    )
    async def ignore_channel(self, ctx, channel_name):
        cur = conn.cursor()

        guild_id = ctx.guild.id
        guild = bot.get_guild(guild_id)

        # Check if Channel exists in Server
        channel_exists = discord.utils.get(guild.channels, name=channel_name)
        if not channel_exists:
            response = f"Channel, {channel_name}, does not exist on this server."
            await ctx.channel.send(f"{response} Please try this command again with a valid channel.")
            logger.info(response)
            return
        
        # Check if this guild has already set a starboard config
        config_check = cur.execute("SELECT guild_id FROM CONFIGS WHERE guild_id=:guild_id", {"guild_id": guild_id}).fetchall()
        if len(config_check)==0:
            await ctx.channel.send(f"Please configure a {vars.bot_name} channel for this server before setting channel exceptions. Use |set to do so.")
        else:
            # Update existing config with new starboard if config present in DB
            try:
                cur.execute(f"""
                    INSERT INTO CHANNEL_EXCEPTIONS VALUES (
                        '{guild_id}{channel_name}',
                        '{guild_id}',
                        '{channel_name}'
                    )
                """)
                conn.commit()
                response = f"{channel_name} has been added to this server's {vars.bot_name} channel exceptions."
                await ctx.channel.send(response)
                logger.info(response)
            except sql.IntegrityError:
                await ctx.channel.send(f'{channel_name} is already being ignored on this server.')
                logger.info(f'{channel_name} already exists in CHANNEL_EXCEPTIONS for server {guild_id}. Skipping...')

        cur.close()

async def setup(bot):
    await bot.add_cog(IgChannelCog(bot))