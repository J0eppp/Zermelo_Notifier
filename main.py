from bot import bot
import db
import os


# Get the discord token
token = os.environ["DISCORD_TOKEN"]

bot.run(token)
