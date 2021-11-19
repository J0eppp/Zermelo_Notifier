from bot import bot
from db import DB
import os
from Browser import Browser

browser = Browser()

# Get the discord token
token = os.environ["DISCORD_TOKEN"]

# Create a database instance
db = DB()
bot.db = db

# Setup the database
# if db.check_db_empty() == True:
#     db.create_database()

# Run the Discord Client
bot.run(token)
