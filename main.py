import os
import discord
from dotenv import load_dotenv
import sqlite3 as sql
import datetime

### GLOBAL  VARS ###
sb_channel_name = "starboard-testing"
reaction_count_threshold = 2

### CONSTRUCTORS ###
load_dotenv()
client = discord.Client()
conn = sql.connect('sb.db')

### SQL DB SETUP ###
# with conn:
#     conn.execute("""
#         CREATE TABLE PINS (
#             id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
#             guild_id INTEGER NOT NULL,
#             channel_id INTEGER NOT NULL,
#             message_id INTEGER NOT NULL,
#             sb_message_id INTEGER NOT NULL
#         );
#     """)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_raw_reaction_add(payload):
    print(f'{payload.member.name} added the reaction, {payload.emoji} to the message with ID: {payload.message_id} in channel, {client.get_channel(payload.channel_id)}')
    guild = client.get_guild(payload.guild_id)
    channel = guild.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)

    # Get Starboard Channel
    sb_channel = discord.utils.get(guild.channels, name=sb_channel_name)
    sb_channel_id = sb_channel.id

    # Get all starred messages in Starboard Channel
    # sb_messages = [message async for message in sb_channel.history(limit=200) b]
    # sb_message_list = [id for message in sb_messages]

    for reaction in message.reactions:

        if reaction.count > reaction_count_threshold:
            print(f'Messaged qualifies for starboard. Posting to starboard channel, {sb_channel_name}...')
            channel = client.get_channel(sb_channel_id)
            # Create Embed Content
            embedVar = discord.Embed(description=message.content, color=0xffffff)
            embedVar.set_author(name=message.author.name, icon_url=message.author.avatar_url_as(size=1024))
            embedVar.insert_field_at(index=1, name="Message", value=f"[Link]({message.jump_url})", inline=True)
            embedVar.insert_field_at(index=2, name="Channel", value=message.channel.name, inline=True)
            embedVar.insert_field_at(index=3, name="Reaction", value=f"{payload.emoji}({reaction.count})")
            starred_message = await channel.send(embed=embedVar)
        
client.run(os.getenv('BS_TOKEN'))