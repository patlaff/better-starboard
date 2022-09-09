from discord.ext import commands
import helpers.vars as vars
from helpers.helpers import createLogger, checkServerConfig, conn
import sqlite3 as sql

logger = createLogger('reactions')

class ReactionManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ### IGNORE REACTION ###
    @commands.command(
        help=f"Use this command to set reaction exceptions for {vars.bot_name}.",
        brief="Use |ignore_reaction <emoji> to add a reaction exception."
    )
    async def ignore_reaction(self, ctx, reaction):
        cur = conn.cursor()

        guild_id = ctx.guild.id
        str_reaction = str(reaction)
        
        # Check if this guild has already set a starboard config
        server_configured = await checkServerConfig(ctx, logger, guild_id)
        if not server_configured:
            cur.close()
            return
        else:
            # Update existing config with new starboard if config present in DB
            try:
                cur.execute(f"INSERT INTO REACTION_EXCEPTIONS VALUES (?, ?, ?)", (
                        f"{guild_id}{str_reaction}",
                        guild_id,
                        str_reaction
                    )
                )
                conn.commit()
                response = f"{str_reaction} has been added to this server's {vars.bot_name} reaction exceptions."
                await ctx.channel.send(response)
                logger.info(response)
            except sql.IntegrityError:
                await ctx.channel.send(f'{str_reaction} is already being ignored on this server.')
                logger.info(f'{str_reaction} already exists in REACTION_EXCEPTIONS for server {guild_id}. Skipping...')

        cur.close()
    
    ### ADD REACTION ###
    @commands.command(
        help=f"Use this command to remove a reaction exception for {vars.bot_name}.",
        brief="Use |add_reaction <emoji> to remove a reaction exception."
    )
    async def add_reaction(self, ctx, reaction):
        cur = conn.cursor()

        guild_id = ctx.guild.id

        # Check if this guild has already set a starboard config
        server_configured = await checkServerConfig(ctx, logger, guild_id)
        if not server_configured:
            cur.close()
            return

        # Check if Channel exists in Server
        reaction_ignored = cur.execute("""
            SELECT reaction
            FROM REACTION_EXCEPTIONS 
            WHERE guild_id=:guild_id AND reaction=:reaction
        """, {"guild_id": guild_id, "reaction": reaction}).fetchone()
        if not reaction_ignored:
            response = f"Reaction, {reaction}, is not ignored on this server."
            await ctx.channel.send(response)
            logger.info(response)
        else:
            # Remove a channel from a server's channel exceptions list
            cur.execute(f"""
                DELETE FROM REACTION_EXCEPTIONS 
                WHERE guild_id=:guild_id AND reaction=:reaction
            """, {"guild_id": guild_id, "reaction": reaction})
            conn.commit()
            response = f"{reaction} has been removed from this server's {vars.bot_name} reaction exceptions."
            await ctx.channel.send(response)
            logger.info(response)

        cur.close()
    
async def setup(bot):
    await bot.add_cog(ReactionManagement(bot))