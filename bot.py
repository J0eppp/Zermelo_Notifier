import discord
from discord.ext import commands
from zermelo import Client

from table2ascii import table2ascii as t2a

import db
import datetime

from Lesson import Lesson

from utils.iso_week import get_current_iso_week


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
        return await ctx.author.send(embed=discord.Embed(title="Error", description="Please only use the signup command in private messages", color=discord.Color.dark_red()))
    if len(args) < 2:
        embed = discord.Embed(
            title="Error, not enough arguments", description=f"Please provide your schoolname and token from the Zermelo Portal and if we have to use single sign on or not, usage: !signup <schoolname> <token>", color=discord.Color.dark_red())
        return await ctx.author.send(embed=embed)

    schoolname = args[0]
    token = args[1]

    # Check if the user has already been signed up
    session = db.Session()
    user = db.User.get_user_by_discord_id(session, ctx.author.id)
    if user != None:
        embed = discord.Embed(title="You already have an account",
                              description=f"You have already signed up to the bot, do you wish to remove your old data and sign up again? If you did this by accident you can ignore this.", color=discord.Color.orange())
        button = discord.ui.Button(
            label="Sign up again", style=discord.ButtonStyle.success, emoji="👋")
        view = discord.ui.View()
        view.add_item(button)
        return await ctx.author.send(embed=embed, view=view)

    # TODO error handling
    client = Client(schoolname)
    auth = client.authenticate(token)
    access_token = auth["access_token"]
    usercode = client.get_user(access_token)[
        "response"]["data"][0]["code"]

    # Create database object
    user = db.User(discord_id=ctx.author.id, date_registered=datetime.date.today(
    ), zermelo_schoolname=schoolname, zermelo_access_token=access_token, zermelo_user_code=usercode)

    db.insert(session, user)
    session.close()

    embed = discord.Embed(
        title="Success!", description=f"The bot retrieved your access token and created a user for you. You can change the notification settings with the !notifications command.", color=discord.Color.green())
    await ctx.author.send(embed=embed)
    client = None
    user = None
    return


# Get today's schedule
@bot.command(name="today", description="Get your schedule for today")
async def today(ctx: commands.Context, *args):
    """Command to get the schedule of today"""
    if ctx.message.guild:
        return await ctx.author.send(embed=discord.Embed(title="Error", description="Please only use the bot in private messages", color=discord.Color.dark_red()))

    # Get the user in the database
    session = db.Session()
    user = db.User.get_user_by_discord_id(session, ctx.author.id)
    client = user.get_client()
    access_token = user.zermelo_access_token
    usercode = user.zermelo_user_code

    now = datetime.datetime.now()
    iso_date = get_current_iso_week()
    print(iso_date)

    # Get the appointments of this week
    appointments = client.get_liveschedule(access_token, iso_date, usercode)[
        "response"]["data"][0]["appointments"]

    def millis_to_datetime(millis) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(
            millis / 1000.0, tz=datetime.timezone.utc)

    lessons_today = []
    for appointment in appointments:
        lesson: Lesson = Lesson.to_lesson(appointment)
        start = lesson.start
        start_datetime = millis_to_datetime(start)
        day = start_datetime.day
        month = start_datetime.month
        year = start_datetime.year
        if day == now.day and month == now.month and year == now.year:
            lessons_today.append(lesson)

    print(lessons_today)

    [print(lesson) for lesson in lessons_today]


# Get the timetable of a week
@bot.command(name="timetable", description="Get the timetable of a specific week")
async def timetable(ctx: commands.Context, *args):
    """Command to get the timetable of a specific week"""
    if ctx.message.guild:
        return await ctx.author.send(embed=discord.Embed(title="Error", description="Please only use the bot in private messages", color=discord.Color.dark_red()))

    week = None

    if len(args) < 1:
        week = get_current_iso_week()
        print(f"Week: {week}")
    else:
        week = args[0]

    # Get the user in the database
    session = db.Session()
    user = db.User.get_user_by_discord_id(session, ctx.author.id)
    client = user.get_client()
    access_token = user.zermelo_access_token
    usercode = user.zermelo_user_code

    # Get the timetable
    appointments = client.get_liveschedule(access_token, week, usercode)[
        "response"]["data"][0]["appointments"]
    # temp = [["" for _ in range(5)] for _ in range(9)]
    temp = [["" for _ in range(9)] for _ in range(5)]
    for appointment in appointments:
        lesson = Lesson.to_lesson(appointment)
        weekday = datetime.datetime.utcfromtimestamp(lesson.start).weekday()
        hour = int(lesson.start_timeslot_name.split("u")[1])
        temp[weekday][hour - 1] = str(lesson)

    headers = ["Monday", "Tuesday", "Wednesday",
               "Thursday", "Friday"]

    for i in range(5):
        header = [headers[i]]
        body = temp[i]
        tbody = [[body[j]] for j in range(len(body))]

        await ctx.send(f"```\n{t2a(header=header, body=tbody)}\n```")
