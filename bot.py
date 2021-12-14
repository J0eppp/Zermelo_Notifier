import discord
from discord.ext import commands

# Local imports
from Browser import Browser
from Queue import Queue
from Task import Task


def get_token_browser(school_name: str, username: str, password: str, single_sign_on: bool) -> dict:
    token = Browser().login_get_token(school_name, username, password, single_sign_on)
    print(f"Token: {token}")
    if len(token) == 0:
        return {"error": "Error, could not find token", "description": "Apologies, I was not able to find the token. Please try again or contact the bot administrator."}
    return {"token": token}


db = None


bot = commands.Bot(command_prefix="!", case_insensitive=True)


queue = Queue()


@bot.event
async def on_ready():
    print("Bot is ready, starting the queue")
    queue.start()
    print("Started the queue")


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
    if len(args) < 3:
        embed = discord.Embed(
            title="Error, not enough arguments", description=f"Please provide your schoolname, username, password and if we have to use single sign on or not, usage: !signup <schoolname> <username> <password> <sso 1 or 0>", color=discord.Color.dark_red())
        return await ctx.author.send(embed=embed)

    # First argument is the schoolname
    school_name = args[0]
    # Second argument is the username
    username = args[1]
    # Third argument is the password
    password = args[2]
    # Fourth argument is SSO
    sso = bool(args[3])

    embed = discord.Embed(
        title="New signup", description=f"Hi thank you for signing up for this service. The bot will try to log into Zermelo, please wait a moment...", color=discord.Color.red())
    await ctx.author.send(embed=embed)

    task = Task(school_name, username, password,
                sso, bot, ctx.message.id)
    print(f"Adding task {task} to queue")
    queue.queue.append(task)

    # result = get_token_browser(school_name, username, password, sso)
    # if result["token"] != None:
    #     await ctx.author.send(result["token"])

    # print(ctx.history)
    # messages = await ctx.channel.history(limit=200).flatten()
    # for msg in messages:
    #     if msg.author.id != bot.user.id:
    #         print(msg.content)
