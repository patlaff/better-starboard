import discord
from discord.ext import commands
from modules import vars
from modules.helpers import createLogger, conn, bot

logger = createLogger('status')

class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help="Use this command to view this server's current configuration status, including starboard channel, threshold, ignored channels, and ignored reactions.",
        brief="Use |status to view this server's current configuration."
    )
    async def status(self, ctx):

        guild_id = ctx.guild.id
        guild = bot.get_guild(guild_id)

        cur = conn.cursor()
        cur.row_factory = lambda cursor, row: row[0]

        # Check if this guild has already set a starboard config
        config_check = cur.execute("SELECT guild_id FROM CONFIGS WHERE guild_id=:guild_id", {"guild_id": guild_id}).fetchall()
        if len(config_check)==0:
            response = f"No {vars.bot_name} configuration found for this server. Please use |set to get started."
            await ctx.channel.send(response)
            logger.info(response)
            return

        sb_channel_name = cur.execute("SELECT sb_channel_name FROM CONFIGS WHERE guild_id=:guild_id", {"guild_id": guild_id}).fetchone()
        reaction_count_threshold = cur.execute("SELECT reaction_count_threshold FROM CONFIGS WHERE guild_id=:guild_id", {"guild_id": guild_id}).fetchone()
        channel_exceptions = cur.execute("SELECT channel_name FROM CHANNEL_EXCEPTIONS WHERE guild_id=:guild_id", {"guild_id": guild_id}).fetchall()
        reaction_exceptions = cur.execute("SELECT reaction FROM REACTION_EXCEPTIONS WHERE guild_id=:guild_id", {"guild_id": guild_id}).fetchall()

        # Create Embed Content
        embedVar = discord.Embed(title=f"{guild.name} {vars.bot_name} configuration:", color=0xffffff)
        embedVar.insert_field_at(index=1, name="Better-Starboard Channel", value=sb_channel_name, inline=True)
        embedVar.insert_field_at(index=2, name="Reaction Count Threshold", value=reaction_count_threshold, inline=True)
        embedVar.insert_field_at(index=3, name='\u200b', value='\u200b', inline=False) # Empty field to force a two column result
        if len(channel_exceptions)==0:
            embedVar.insert_field_at(index=4, name="Channel Exceptions", value='None', inline=True)
        else:
            embedVar.insert_field_at(index=4, name="Channel Exceptions", value=''.join((f"- {i}\n" for i in channel_exceptions)), inline=True)
        if len(reaction_exceptions)==0:
            embedVar.insert_field_at(index=5, name="Reaction Exceptions", value='None', inline=True)
        else:
            embedVar.insert_field_at(index=5, name="Reaction Exceptions", value=''.join((f"- {i}\n" for i in reaction_exceptions)), inline=True)
        
        await ctx.channel.send(embed=embedVar)

        cur.close()

async def setup(bot):
    await bot.add_cog(StatusCog(bot))