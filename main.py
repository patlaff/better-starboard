import os
import discord
import logging
from sqlTables import createTables
import sqlite3 as sql
from dotenv import load_dotenv

### CONFIG ###
log_folder = "logs"
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler = logging.FileHandler(f'{log_folder}/bs.log')
handler.setFormatter(formatter)

logger = logging.getLogger('bs_logger')
logger.setLevel(logging.INFO)
logger.addHandler(handler)

### GLOBAL VARS ###
bot_name = 'better-starboard'
set_string = '|set'
thresh_string = '|threshold'
default_reaction_count_threshold = 3

### CONSTRUCTORS ###
createTables()
load_dotenv()
client = discord.Client(intents=discord.Intents.default())
conn = sql.connect('sb.db')

### GLOBAL FUNCTIONS ###
def createEmbed(message, payload, reaction):
    # Create Embed Content
    embedVar = discord.Embed(description=message.content, color=0xffffff)
    embedVar.set_author(name=message.author.name, icon_url=message.author.avatar_url_as(size=1024))
    embedVar.insert_field_at(index=1, name="Message", value=f"[Link]({message.jump_url})", inline=True)
    embedVar.insert_field_at(index=2, name="Channel", value=message.channel.name, inline=True)
    embedVar.insert_field_at(index=3, name="Reaction", value=f"{payload.emoji}({reaction.count})")
    return embedVar

def insertConfig(guild_id, sb_channel_name, reaction_count_threshold, message):
    return

def updateConfig(guild_id, sb_channel_name, reaction_count_threshold, message):
    return


### CLIENT EVENT ACTIONS ###
@client.event
async def on_ready():
    logger.info('We have logged in as {0.user}'.format(client))


# @bot.command()
# @commands.has_permissions([manage_channels=True])
@client.event
async def on_message(message):
    # Make sure message was not sent by this bot
    if message.author == client.user:
        return
    
    # Make sure author of this message has the appropriate role

    ## Set starboard channel for server
    if message.content.startswith(set_string):
        cur = conn.cursor()

        guild_id = message.guild.id
        guild = client.get_guild(guild_id)
        sb_channel_name = message.content.replace(set_string,'').strip()

        # Check if Channel exists in Server
        try:
            sb_channel = discord.utils.get(guild.channels, name=sb_channel_name)
        except:
            logger.info(f"Channel, {sb_channel_name}, does not exist on this server.")
            await message.channel.send(f"Channel, {sb_channel_name}, does not exist on this server. Please try this command again with a valid channel.")
            return

        # Check if this guild has already set a starboard config
        config_check = cur.execute("SELECT guild_id FROM CONFIGS WHERE guild_id=:guild_id", {"guild_id": guild_id}).fetchall()
        if len(config_check)==0:
            # Insert initial config with default reaction_count_threshold if no config present in DB
            cur.execute(f"""
                INSERT INTO CONFIGS VALUES (
                    '{guild_id}',
                    '{sb_channel_name}',
                    '{default_reaction_count_threshold}'
                )
            """)
            conn.commit()
            await message.channel.send(f"Channel, {sb_channel_name}, has been added as this server's {bot_name}. Default reaction threshold was set to {default_reaction_count_threshold}. Use {thresh_string} to set a custom threshold.")
        else:
            # Update existing config with new starboard if config present in DB
            cur.execute(f"""
                UPDATE CONFIGS
                SET sb_channel_name = {sb_channel_name}
                WHERE
                    guild_id=:guild_id
            """, {"guild_id": guild_id})
            conn.commit()
            await message.channel.send(f"Channel, {sb_channel_name}, has been updated as this server's {bot_name}.")

    # Set custom reaction count threshold for server
    if message.content.startswith(thresh_string):
        cur = conn.cursor()

        guild_id = message.guild.id
        guild = client.get_guild(guild_id)
        reaction_count_threshold = message.content.replace(thresh_string,'').strip()
        
        # Check if this guild has already set a starboard config
        config_check = cur.execute("SELECT guild_id FROM CONFIGS WHERE guild_id=:guild_id", {"guild_id": guild_id}).fetchall()
        if len(config_check)==0:
            await message.channel.send(f"Please configure a {bot_name} channel for this server before setting a custom reaction count threshold. Use {set_string} to do so.")
        else:
            # Update existing config with new starboard if config present in DB
            cur.execute(f"""
                UPDATE CONFIGS
                SET reaction_count_threshold = {reaction_count_threshold}
                WHERE
                    guild_id=:guild_id
            """, {"guild_id": guild_id})
            conn.commit()
            await message.channel.send(f"A new reaction count threshold of {reaction_count_threshold} has been updated for this server's {bot_name}.")

@client.event
async def on_raw_reaction_add(payload):

    # Commit some common vars
    guild_id = payload.guild_id
    channel_id = payload.channel_id
    message_id = payload.message_id

    # Get context objects
    guild = client.get_guild(guild_id)
    channel = guild.get_channel(channel_id)
    message = await channel.fetch_message(message_id)

    # Open DB Cursor
    cur = conn.cursor()
    cur.row_factory = lambda cursor, row: row[0]

    # Check if server has been configured yet. Get starboard channel name if so. Do nothing if not.
    config_check = cur.execute("SELECT guild_id FROM CONFIGS WHERE guild_id=:guild_id", {"guild_id": guild_id}).fetchall()
    if len(config_check)==0:
        return
    else:
        sb_channel_name = cur.execute("SELECT sb_channel_name FROM CONFIGS WHERE guild_id=:guild_id", {"guild_id": guild_id}).fetchone()

    # Log reaction
    logger.info(f'{payload.member.name} added the reaction, {payload.emoji} to the message with ID: {payload.message_id} in channel, {client.get_channel(payload.channel_id)}')
   
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
            logger.info(f'Message already starred.')

            # Update starred message with new reaction count
            if reaction.count >= reaction_count_threshold:
                logger.info(f'Updating reaction count for message, {message_id} to {reaction.count}...')
                starred_id = cur.execute("SELECT sb_message_id FROM PINS WHERE message_id=:message_id", {"message_id": message_id}).fetchone()
                starred_message = await sb_channel.fetch_message(starred_id)

                embedVar = createEmbed(message, payload, reaction)
                await starred_message.edit(embed=embedVar)

                return

        if reaction.count >= reaction_count_threshold:
            logger.info(f'Messaged qualifies for starboard. Posting to starboard channel, {sb_channel_name}...')
            channel = client.get_channel(sb_channel_id)

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
        
client.run(os.getenv('BS_TOKEN'))
