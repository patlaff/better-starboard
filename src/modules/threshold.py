from discord.ext import commands
from modules import vars
from modules.helpers import createLogger, conn, bot

logger = createLogger('threshold')

class ThreshCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help="Use this command to set the reaction threshold for posting messages to your starboard. Default is 5.",
        brief="Use |threshold <int> to set the number of reactions needed."
    )
    async def threshold(self, ctx, reaction_count_threshold):
        cur = conn.cursor()

        guild_id = ctx.guild.id
        guild = bot.get_guild(guild_id)
        
        # Check if this guild has already set a starboard config
        config_check = cur.execute("SELECT guild_id FROM CONFIGS WHERE guild_id=:guild_id", {"guild_id": guild_id}).fetchall()
        if len(config_check)==0:
            await ctx.channel.send(f"Please configure a {vars.bot_name} channel for this server before setting a custom reaction count threshold. Use |set to do so.")
        else:
            # Update existing config with new starboard if config present in DB
            cur.execute(f"""
                UPDATE CONFIGS
                SET reaction_count_threshold = {reaction_count_threshold}
                WHERE
                    guild_id=:guild_id
            """, {"guild_id": guild_id})
            conn.commit()
            response = f"A new reaction count threshold of {reaction_count_threshold} has been updated for this server's {vars.bot_name}."
            await ctx.channel.send(response)
            logger.info(response)

        cur.close()

async def setup(bot):
    await bot.add_cog(ThreshCog(bot))