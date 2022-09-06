import os
import sys
import logging
import discord
from discord.ext import commands
import sqlite3 as sql

def createDir(folder):
    ## Create log folder if not exists ##
    path = os.path.join(sys.path[0], folder)
    # Check whether the specified path exists or not
    path_exist = os.path.exists(path)
    # Create log path if not exists
    if not path_exist:
        os.makedirs(path)
        print(f"Required path {path} not detected, so we created it!")

    return path

def createLogger(logger_name):
    # Configure logger
    log_path = createDir("logs")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler = logging.FileHandler(os.path.join(log_path, f'{logger_name}.log'))
    handler.setFormatter(formatter)
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger

def createDbConn(folder_name='db', db_name='bs'):
    ### CONSTRUCTORS ###
    db_folder = createDir(folder_name)
    conn = sql.connect(f'{db_folder}/{db_name}.db')
    return conn

conn = createDbConn()

def createBot():
    # Create and configure Discord bot
    intents = discord.Intents.default()
    intents.message_content = True
    help_command = commands.DefaultHelpCommand(
        no_category = 'Commands'
    )
    bot = commands.Bot(
        command_prefix="|",
        intents=intents,
        help_command = help_command
    )
    return bot

bot = createBot()

def createEmbed(message, payload, reaction):
    # Create Embed Content
    embedVar = discord.Embed(description=message.content, color=0xffffff)
    embedVar.set_author(name=message.author.name, icon_url=message.author.display_avatar)
    embedVar.insert_field_at(index=1, name="Message", value=f"[Link]({message.jump_url})", inline=True)
    embedVar.insert_field_at(index=2, name="Channel", value=message.channel.name, inline=True)
    embedVar.insert_field_at(index=3, name="Reaction", value=f"{payload.emoji}({reaction.count})")
    return embedVar