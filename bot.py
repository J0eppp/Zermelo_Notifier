import discord
from discord.ext import commands


bot = commands.Bot(command_prefix="!", case_insensitive=True)


@bot.event
async def on_ready():
    print("ready")


@bot.command(name="hello", description="Greet the user!")
async def hello(ctx):
    if not ctx.message.guild:
        await ctx.send(f"Hello!")
    else:
        await ctx.send(f"Hello {ctx.author.name}!")


# Command to sign up to the "service"
@bot.command(name="signup", description="Sign up to the bot")
async def signup(ctx):
    author = ctx.author
    send = author.send
    await send("Hi, thank you for signing up to this service")
