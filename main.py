from bot import bot
import os

# Get the discord token
token = os.environ["DISCORD_TOKEN"]


# # Run the Discord Client
# client = Client()
bot.run(token)
