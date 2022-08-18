import os
import discord
from dotenv import load_dotenv

### CONSTRUCTORS ###
load_dotenv()
client = discord.Client()

### GLOBAL VARS ###
sb_channel_name = "starboard-testing"
reaction_count_threshold = 0

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        print(f'Messaged Received from {message.author}! Sending response...')
        #await message.channel.send('Hello!')

@client.event
async def on_raw_reaction_add(payload):
    print(f'{payload.member.name} added the reaction, {payload.emoji} to the message with ID: {payload.message_id} in channel, {payload.channel_id}')
    guild = client.get_guild(payload.guild_id)
    channel = guild.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    print(message.reactions)

    # Get Starboard Channel
    sb_channel = discord.utils.get(guild.channels, name=sb_channel_name)
    sb_channel_id = sb_channel.id

    for reaction in message.reactions:
        if reaction.count > reaction_count_threshold:
            print(f'Messaged qualifies for starboard. Posting to starboard channel, ...')
            channel = client.get_channel(sb_channel_id)
            await channel.send('Hello!')
        
client.run(os.getenv('BS_TOKEN'))