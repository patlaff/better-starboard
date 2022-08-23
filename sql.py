import sqlite3 as sql

conn = sql.connect('sb.db')

## SQL DB SETUP ###
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