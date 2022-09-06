from discord.ext import commands
from modules import vars
from modules.helpers import createLogger, conn
import sqlite3 as sql

logger = createLogger('ignore_reaction')

class IgReactionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help=f"Use this command to set reaction exceptions for {vars.bot_name}.",
        brief="Use |ignore_reaction <emoji> to add a reaction exception."
    )
    async def ignore_reaction(self, ctx, reaction):
        cur = conn.cursor()

        guild_id = ctx.guild.id
        str_reaction = str(reaction)
        
        # Check if this guild has already set a starboard config
        config_check = cur.execute("SELECT guild_id FROM CONFIGS WHERE guild_id=:guild_id", {"guild_id": guild_id}).fetchall()
        if len(config_check)==0:
            await ctx.channel.send(f"Please configure a {vars.bot_name} channel for this server before setting channel exceptions. Use |set to do so.")
        else:
            # Update existing config with new starboard if config present in DB
            try:
                cur.execute(f"""
                    INSERT INTO REACTION_EXCEPTIONS VALUES (
                        '{guild_id}{str_reaction}',
                        '{guild_id}',
                        '{str_reaction}'
                    )
                """)
                conn.commit()
                response = f"{str_reaction} has been added to this server's {vars.bot_name} reaction exceptions."
                await ctx.channel.send(response)
                logger.info(response)
            except sql.IntegrityError:
                await ctx.channel.send(f'{str_reaction} is already being ignored on this server.')
                logger.info(f'{str_reaction} already exists in REACTION_EXCEPTIONS for server {guild_id}. Skipping...')

        cur.close()
    
async def setup(bot):
    await bot.add_cog(IgReactionCog(bot))