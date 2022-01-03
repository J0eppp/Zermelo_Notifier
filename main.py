from bot import bot
import db
import os

from utils.log import setup, info
import logging
logger = logging.getLogger("bot")


setup()

# Get the discord token
token = os.environ["DISCORD_TOKEN"]

logger.info(f"Starting the bot")
bot.run(token)
