import discord
from discord.ext import commands
from zermelo import Client

from typing import List

import db
import datetime


# db = None
bot = commands.Bot(command_prefix="!", case_insensitive=True)


@bot.event
async def on_ready():
    print("Bot is ready")


@bot.command(name="hello", description="Greet the user!")
async def hello(ctx: commands.Context):
    if not ctx.message.guild:
        await ctx.send(f"Hello!")
    else:
        await ctx.send(f"Hello {ctx.author.name}!")


# Command to sign up to the "service"
@bot.command(name="signup", description="Sign up to the bot")
async def signup(ctx: commands.Context, *args):
    """Command to sign up to the "service"""
    if ctx.message.guild:
        return await ctx.author.send(embed=discord.Embed(title="Error", description="Please only use the signup command in private", color=discord.Color.red()))
    if len(args) < 1:
        embed = discord.Embed(
            title="Error, not enough arguments", description=f"Please provide your schoolname and token from the Zermelo Portal and if we have to use single sign on or not, usage: !signup <schoolname> <token>", color=discord.Color.dark_red())
        return await ctx.author.send(embed=embed)

    schoolname = args[0]
    token = args[1]

    # TODO error handling
    client = Client(schoolname)
    auth = client.authenticate(token)
    access_token = auth["access_token"]

    # Create database object
    user = db.User(discord_id=ctx.author.id, date_registered=datetime.date.today(
    ), zermelo_schoolname=schoolname, zermelo_access_token=access_token)

    session = db.Session()
    db.insert(session, user)
    session.close()

    embed = discord.Embed(
        title="Success!", description=f"The bot retrieved your access token and created a user for you. You can change the notification settings with the !notifications command.", color=discord.Color.green())
    await ctx.author.send(embed=embed)
