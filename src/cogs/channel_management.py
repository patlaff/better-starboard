import discord
from discord.ext import commands
import helpers.vars as vars
from helpers.helpers import createLogger, checkServerConfig, conn
import sqlite3 as sql

logger = createLogger('channels')

class ChannelManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ### IGNORE CHANNEL ###
    @commands.has_permissions(
        manage_channels=True,
        manage_messages=True
    )
    @commands.command(
        help=f"Use this command to set channel exceptions for {vars.bot_name}.",
        brief="Use |ignore_channel <channel_name> to add a channel exception."
    )
    async def ignore_channel(self, ctx, channel_name):
        cur = conn.cursor()

        guild_id = ctx.guild.id
        guild = self.bot.get_guild(guild_id)

        # Check if Channel exists in Server
        channel_exists = discord.utils.get(guild.channels, name=channel_name)
        if not channel_exists:
            response = f"Channel, {channel_name}, does not exist on this server."
            await ctx.channel.send(f"{response} Please try this command again with a valid channel.")
            logger.info(response)
            return
        
        # Check if this guild has already set a starboard config
        server_configured = await checkServerConfig(ctx, logger, guild_id)
        if not server_configured:
            cur.close()
            return
        else:
            # Add new Channel Exception if it does not already exists
            try:
                cur.execute("INSERT INTO CHANNEL_EXCEPTIONS VALUES (?, ?, ?)", (
                        f'{guild_id}{channel_name}',
                        guild_id,
                        channel_name
                    )
                )
                conn.commit()
                response = f"{channel_name} has been added to this server's {vars.bot_name} channel exceptions."
                await ctx.channel.send(response)
                logger.info(response)
            except sql.IntegrityError:
                await ctx.channel.send(f'{channel_name} is already being ignored on this server.')
                logger.info(f'{channel_name} already exists in CHANNEL_EXCEPTIONS for server {guild_id}. Skipping...')

        cur.close()
    
    ### ADD CHANNEL ###
    @commands.has_permissions(
        manage_channels=True,
        manage_messages=True
    )
    @commands.command(
        help=f"Use this command to remove a channel exception for {vars.bot_name}.",
        brief="Use |add_channel <channel_name> to remove a channel exception."
    )
    async def add_channel(self, ctx, channel_name):
        cur = conn.cursor()

        guild_id = ctx.guild.id

        # Check if this guild has already set a starboard config
        server_configured = await checkServerConfig(ctx, logger, guild_id)
        if not server_configured:
            cur.close()
            return

        # Check if Channel exists in Server
        channel_ignored = cur.execute("""
            SELECT channel_name 
            FROM CHANNEL_EXCEPTIONS 
            WHERE guild_id=:guild_id AND channel_name=:channel_name
        """, {"guild_id": guild_id, "channel_name": channel_name}).fetchone()
        if not channel_ignored:
            response = f"Channel, {channel_name}, is not ignored on this server."
            await ctx.channel.send(response)
            logger.info(response)
        else:
            # Remove a channel from a server's channel exceptions list
            cur.execute(f"""
                DELETE FROM CHANNEL_EXCEPTIONS 
                WHERE guild_id=:guild_id AND channel_name=:channel_name
            """, {"guild_id": guild_id, "channel_name": channel_name})
            conn.commit()
            response = f"{channel_name} has been removed from this server's {vars.bot_name} channel exceptions."
            await ctx.channel.send(response)
            logger.info(response)

        cur.close()

async def setup(bot):
    await bot.add_cog(ChannelManagement(bot))