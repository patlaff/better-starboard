import sqlite3 as sql
from modules.helpers import createLogger, conn

### CONFIG ###
logger = createLogger('sql')

## SQL DB SETUP ###
def createTables():

    ### CONSTRUCTORS ###
    cur = conn.cursor()
    
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
            cur.execute("""
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
            cur.execute("""
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
            cur.execute("""
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
            cur.execute("""
                CREATE TABLE REACTION_EXCEPTIONS (
                    id TEXT NOT NULL PRIMARY KEY,
                    guild_id INTEGER NOT NULL,
                    reaction TEXT NOT NULL
                );
            """)
    
    cur.close()