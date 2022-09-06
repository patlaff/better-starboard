import discord
from discord.ext import commands
from modules import vars
from modules.helpers import createLogger, createEmbed, conn, bot

logger = createLogger('reactions')

class ReactionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        # Commit some common vars
        guild_id = payload.guild_id
        channel_id = payload.channel_id
        message_id = payload.message_id
        reaction = str(payload.emoji)

        # Get context objects
        guild = bot.get_guild(guild_id)
        channel = guild.get_channel(channel_id)
        message = await channel.fetch_message(message_id)

        # Open DB Cursor
        cur = conn.cursor()
        cur.row_factory = lambda cursor, row: row[0]

        # Check if channel is being ignored on this server
        channel_check = cur.execute("SELECT channel_name FROM CHANNEL_EXCEPTIONS WHERE guild_id=:guild_id", {"guild_id": guild_id}).fetchall()
        if channel.name in channel_check:
            logger.info(f'{channel.name} ignored on server {guild_id}. Exiting...')
            return
        
        # Check if reaction is being ignored on this server
        reaction_check = cur.execute("SELECT reaction FROM REACTION_EXCEPTIONS WHERE guild_id=:guild_id", {"guild_id": guild_id}).fetchall()
        if reaction in reaction_check:
            logger.info(f'{reaction} ignored on server {guild_id}. Exiting...')
            return

        # Check if server has been configured yet. Get starboard channel name if so. Do nothing if not.
        config_check = cur.execute("SELECT guild_id FROM CONFIGS WHERE guild_id=:guild_id", {"guild_id": guild_id}).fetchall()
        if len(config_check)==0:
            return
        else:
            sb_channel_name = cur.execute("SELECT sb_channel_name FROM CONFIGS WHERE guild_id=:guild_id", {"guild_id": guild_id}).fetchone()

        # Log reaction
        logger.info(f'{payload.member.name} added the reaction, {payload.emoji}, to the message with ID, {payload.message_id}, in channel, {bot.get_channel(payload.channel_id)}')

        # Get Starboard Channel
        sb_channel = discord.utils.get(guild.channels, name=sb_channel_name)
        sb_channel_id = sb_channel.id

        # Get server-specific reaction_count_threshold
        reaction_count_threshold = cur.execute("SELECT reaction_count_threshold FROM CONFIGS WHERE guild_id=:guild_id", {"guild_id": guild_id}).fetchone()

        # Get all starred messages in Starboard Channel from DB
        message_ids = cur.execute("SELECT message_id FROM PINS WHERE guild_id=:guild_id", {"guild_id": guild_id}).fetchall()
        #logger.info(f"Starred Messages: {message_ids}")

        for reaction in message.reactions:

            if message_id in message_ids:
                logger.info(f'Message, {message_id}, already starred.')

                # Update starred message with new reaction count
                if reaction.count >= reaction_count_threshold:
                    logger.info(f'Updating reaction count for message, {message_id} to {reaction.count}...')
                    starred_id = cur.execute("SELECT sb_message_id FROM PINS WHERE message_id=:message_id", {"message_id": message_id}).fetchone()
                    starred_message = await sb_channel.fetch_message(starred_id)

                    embedVar = createEmbed(message, payload, reaction)
                    await starred_message.edit(embed=embedVar)

                    return

            if reaction.count >= reaction_count_threshold:
                logger.info(f'Messaged qualifies for {vars.bot_name}. Posting to {vars.bot_name} channel, {sb_channel_name}...')
                channel = bot.get_channel(sb_channel_id)

                embedVar = createEmbed(message, payload, reaction)
                starred_message = await channel.send(embed=embedVar)

                cur.execute(f"""
                    INSERT INTO PINS VALUES (
                        '{starred_message.id}',
                        '{guild_id}',
                        '{channel_id}',
                        '{message_id}'
                    )
                """)
                conn.commit()
        
        cur.close()

async def setup(bot):
    await bot.add_cog(ReactionCog(bot))