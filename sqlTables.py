import os
import sys
import sqlite3 as sql
import logging
from helpers import createLogDir

### CONFIG ###
log_folder = createLogDir("logs")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler = logging.FileHandler(os.path.join(sys.path[0], f'{log_folder}/sql.log'))
handler.setFormatter(formatter)

logger = logging.getLogger('sql_logger')
logger.setLevel(logging.INFO)
logger.addHandler(handler)

### CONSTRUCTORS ###
conn = sql.connect('sb.db')
cur = conn.cursor()

## SQL DB SETUP ###
def createTables():
    
    ## PINS ##
    # with conn:
    #     conn.execute("DROP TABLE PINS;")
    
    with conn:
        cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='PINS'")

    if cur.fetchone()[0]==1:
        logger.info('Table, PINS, already exists.')
    else:
        logger.info('Table does not exist. Creating table, PINS...')
        with conn:
            conn.execute("""
                CREATE TABLE PINS (
                    sb_message_id INTEGER NOT NULL PRIMARY KEY,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    message_id INTEGER NOT NULL
                );
            """)

    ## CONFIGS ##
    # with conn:
    #     conn.execute("DROP TABLE CONFIGS;")
    
    with conn:
        cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='CONFIGS'")

    if cur.fetchone()[0]==1:
        logger.info('Table, CONFIGS, already exists.')
    else:
        logger.info('Table does not exist. Creating table, CONFIGS...')
        with conn:
            conn.execute("""
                CREATE TABLE CONFIGS (
                    guild_id INTEGER NOT NULL PRIMARY KEY,
                    sb_channel_name TEXT NOT NULL,
                    reaction_count_threshold INTEGER NOT NULL
                );
            """)

    ## CHANNEL_EXCEPTIONS ##
    # with conn:
    #     conn.execute("DROP TABLE CHANNEL_EXCEPTIONS;")
    
    with conn:
        cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='CHANNEL_EXCEPTIONS'")

    if cur.fetchone()[0]==1:
        logger.info('Table, CHANNEL_EXCEPTIONS, already exists.')
    else:
        logger.info('Table does not exist. Creating table, CHANNEL_EXCEPTIONS...')
        with conn:
            conn.execute("""
                CREATE TABLE CHANNEL_EXCEPTIONS (
                    id TEXT NOT NULL PRIMARY KEY,
                    guild_id INTEGER NOT NULL,
                    channel_name TEXT NOT NULL
                );
            """)

    ## REACTION_EXCEPTIONS ##
    # with conn:
    #     conn.execute("DROP TABLE REACTION_EXCEPTIONS;")
    
    with conn:
        cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='REACTION_EXCEPTIONS'")

    if cur.fetchone()[0]==1:
        logger.info('Table, REACTION_EXCEPTIONS, already exists.')
    else:
        logger.info('Table does not exist. Creating table, REACTION_EXCEPTIONS...')
        with conn:
            conn.execute("""
                CREATE TABLE REACTION_EXCEPTIONS (
                    id TEXT NOT NULL PRIMARY KEY,
                    guild_id INTEGER NOT NULL,
                    reaction TEXT NOT NULL
                );
            """)