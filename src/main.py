import os
import discord
from dotenv import load_dotenv

load_dotenv()

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        print(f'Messaged Received from {message.author}! Sending response...')
        await message.channel.send('Hello!')
        
client.run(os.getenv('BS_TOKEN'))