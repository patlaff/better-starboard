import discord
from discord.ext import commands
import helpers.vars as vars
from helpers.helpers import createLogger, checkServerConfig, conn

logger = createLogger('config')

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ### SET ###
    @commands.has_permissions(
        manage_channels=True,
        manage_messages=True
    )
    @commands.command(
        help="Use this command to set the starboard channel for this server. Ex: |set <channel> Ex: |set starboard-channel",
	    brief="Use |set <channel_name> to set the starboard channel for this server."
    )
    async def set(self, ctx, channel_name):
        cur = conn.cursor()

        guild_id = ctx.guild.id
        guild = self.bot.get_guild(guild_id)
        sb_channel_name = channel_name

        # Check if Channel exists in Server
        channel_exists = discord.utils.get(guild.channels, name=sb_channel_name)
        if not channel_exists:
            response = f"Channel, {sb_channel_name}, does not exist on this server."
            await ctx.channel.send(f"{response} Please try this command again with a valid channel.")
            logger.info(response)
            return

        # Check if this guild has already set a starboard config
        config_check = cur.execute("SELECT guild_id FROM CONFIGS WHERE guild_id=:guild_id", {"guild_id": guild_id}).fetchall()
        if len(config_check)==0:
            # Insert initial config with default reaction_count_threshold if no config present in DB
            cur.execute(f"INSERT INTO CONFIGS VALUES (?, ?, ?)", (
                guild_id,
                sb_channel_name,
                vars.default_reaction_count_threshold
                )
            )
            conn.commit()
            response = f"Channel, {sb_channel_name}, has been added as this server's {vars.bot_name}. Default reaction threshold was set to {vars.default_reaction_count_threshold}. Use |threshold to set a custom threshold."
            await ctx.channel.send(response)
            logger.info(response)
        else:
            # Update existing config with new starboard if config present in DB
            cur.execute(f"""
                UPDATE CONFIGS
                SET sb_channel_name=:sb_channel_name
                WHERE guild_id=:guild_id
            """, {"guild_id": guild_id, "sb_channel_name": sb_channel_name})
            conn.commit()
            response = f"Channel, {sb_channel_name}, has been updated as this server's {vars.bot_name}."
            await ctx.channel.send(response)
            logger.info(response)

        cur.close()

    ### THRESHOLD ###
    @commands.has_permissions(
        manage_channels=True,
        manage_messages=True
    )
    @commands.command(
        help="Use this command to set the reaction threshold for posting messages to your starboard. Default is 5.",
        brief="Use |threshold <int> to set the number of reactions needed."
    )
    async def threshold(self, ctx, reaction_count_threshold):
        cur = conn.cursor()

        guild_id = ctx.guild.id
        
        # Check if this guild has already set a starboard config
        server_configured = await checkServerConfig(ctx, logger, guild_id)
        if not server_configured:
            cur.close()
            return
        else:
            # Update existing config with new starboard if config present in DB
            cur.execute(f"""
                UPDATE CONFIGS
                SET reaction_count_threshold=:reaction_count_threshold
                WHERE guild_id=:guild_id
            """, {"guild_id": guild_id, "reaction_count_threshold": reaction_count_threshold})
            conn.commit()
            response = f"A new reaction count threshold of {reaction_count_threshold} has been updated for this server's {vars.bot_name}."
            await ctx.channel.send(response)
            logger.info(response)

        cur.close()


async def setup(bot):
    await bot.add_cog(Config(bot))