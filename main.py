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
sb_channel_name = "starboard-testing"
reaction_count_threshold = 3

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

### CLIENT EVENT ACTIONS ###
@client.event
async def on_ready():
    logger.info('We have logged in as {0.user}'.format(client))

# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return

#     if message.content.startswith('⭐'):
#         ### SET sb_channel_name & reaction_count_threshold

@client.event
async def on_raw_reaction_add(payload):
    logger.info(f'{payload.member.name} added the reaction, {payload.emoji} to the message with ID: {payload.message_id} in channel, {client.get_channel(payload.channel_id)}')

    # Open DB Cursor
    cur = conn.cursor()

    # Commit some common vars
    guild_id = payload.guild_id
    channel_id = payload.channel_id
    message_id = payload.message_id

    # Get context objects
    guild = client.get_guild(guild_id)
    channel = guild.get_channel(channel_id)
    message = await channel.fetch_message(message_id)

    # Get Starboard Channel
    sb_channel = discord.utils.get(guild.channels, name=sb_channel_name)
    sb_channel_id = sb_channel.id

    # Get all starred messages in Starboard Channel from DB
    cur.row_factory = lambda cursor, row: row[0]
    message_ids = cur.execute("SELECT message_id FROM PINS WHERE guild_id=:guild_id", {"guild_id": guild_id}).fetchall()
    logger.info(f"Starred Messages: {message_ids}")

    for reaction in message.reactions:

        if message_id in message_ids:
            logger.info(f'Message already starred. Updating reaction count for message, {message_id} to {reaction.count}...')

            # Update starred message with new reaction count
            if reaction.count >= reaction_count_threshold:
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
