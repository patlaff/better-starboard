import sqlite3 as sql
import logging

### CONFIG ###
log_folder = "logs"
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler = logging.FileHandler(f'{log_folder}/sql.log')
handler.setFormatter(formatter)

logger = logging.getLogger('sql_logger')
logger.setLevel(logging.INFO)
logger.addHandler(handler)

### CONSTRUCTORS ###
conn = sql.connect('sb.db')
cur = conn.cursor()

## SQL DB SETUP ###
def createTables():
    # with conn:
    #     conn.execute("DROP TABLE PINS;")
    #

    with conn:
        cur.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='PINS'")

    if cur.fetchone()[0]==1:
        logger.info('Table, PINS, already exists.')
    else:
        logger.info('Table does not exist. Creating table, PINS...')
        with conn:
            conn.execute("""
                CREATE TABLE PINS (
                    sb_message_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    message_id INTEGER NOT NULL
                );
            """)