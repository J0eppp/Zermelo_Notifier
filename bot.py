import discord
from discord.ext import commands


db = None


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
async def signup(ctx, *args):
    if len(args) < 3:
        embed = discord.Embed(
            title="Error, not enough arguments", description=f"Please provide your schoolname, username and password, usage: !signup <schoolname> <username> <password>", color=discord.Color.dark_red())
        return await ctx.author.send(embed=embed)
    # First argument is the schoolname
    school_name = args[0]
    print(f"Schoolname: {school_name}")
    # Second argument is the username
    username = args[1]
    print(f"Username: {username}")
    # Third argument is the password
    password = args[2]
    print(f"Password: {password}")
    print(args)
    embed = discord.Embed(
        title="New signup", description=f"Hi thank you for signing up for this service. The bot will try to log into Zermelo, please wait a moment...", color=discord.Color.red())
    await ctx.author.send(embed=embed)
