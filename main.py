from threading import Thread
import asyncio

from bot import bot
from db import DB
import os
from Browser import Browser

# browser = Browser()

# Get the discord token
token = os.environ["DISCORD_TOKEN"]

# Create a database instance
db = DB()
bot.db = db

# Setup the database
# if db.check_db_empty() == True:
#     db.create_database()

# Run the Discord Client
bot_loop = asyncio.get_event_loop()
bot_loop.create_task(bot.run(token))
bot_thread = Thread(target=bot_loop.run_forever)
bot_thread.start()

while True:
    continue
