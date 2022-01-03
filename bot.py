import discord
from discord.ext import commands
from discord.ext.commands.core import check
from zermelo import Client

import logging
from typing import List

from enum import Enum

from table2ascii import table2ascii as t2a

import db
from db import User, Reaction, ReactionActions, Session
import datetime

from Lesson import Lesson

from utils.iso_week import get_current_iso_week
from utils.millis_to_datetime import millis_to_datetime

from constants import WEEKDAYS, NO

import asyncio
from time import time
import os

discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename=os.environ["LOG_PATH_DISCORD"], encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
discord_logger.addHandler(handler)

bot = commands.Bot(command_prefix="!", case_insensitive=True)

logger = logging.getLogger("bot")


class NotificationTypes(Enum):
    CLASS_STARTS_SOON = 0


# This method executes code every 10 seconds
async def bot_loop():
    start_time = None
    end_time = None

    def check_notification(user: User) -> dict:
        lessons: List[Lesson] = user.get_lessons(get_current_iso_week())
        for lesson in lessons:
            start = datetime.datetime.utcfromtimestamp(int(lesson.start))
            before = user.notify_before_start
            notify_time = start - datetime.timedelta(minutes=before)
            if user.last_notification_before_start == None:
                user.last_notification_before_start = datetime.datetime(
                    1970, 1, 1)
            print(f"last_notif: {user.last_notification_before_start}")
            print(f"notify_time: {notify_time}")
            print(f"start: {start}")

            if user.last_notification_before_start < notify_time < start > datetime.datetime.now():
                # Send notification
                return {"lesson": lesson, "notification_type": NotificationTypes.CLASS_STARTS_SOON}

        return None

    while True:
        start_time = time()
        logger.info("Running bot_loop()")
        # Check if we need to send a notification to someone
        session = Session()
        for user in User.get_users(session):
            check = check_notification(user)
            if check == None:
                continue
            # We need to notify, check variable contains info about the notification
            print("NOTIFYING USER")
            print(check)
            d_user = await bot.fetch_user(user.discord_id)
            lesson: Lesson = check["lesson"]
            title = None
            description = None
            color = None
            if check["notification_type"] == NotificationTypes.CLASS_STARTS_SOON:
                title = "Class starts soon"
                description = f"Your {', '.join(lesson.subjects)} lesson{'s' if len(lesson.subjects) > 1 else ''} starts at {datetime.datetime.strftime(datetime.datetime.utcfromtimestamp(int(lesson.start)), '%H:%M')} in {', '.join(lesson.locations)}"
                color = discord.Color.orange()
            embed = discord.Embed(
                title=title, description=description, color=color)
            await d_user.send(embed=embed)
            user.last_notification_before_start = datetime.datetime.now()
            db.merge(session, user)
        session.close()
        end_time = time()
        delay = 60 - (end_time - start_time)
        await asyncio.sleep(delay)


@bot.event
async def on_ready():
    print("Bot is ready")
    logger.info("Bot is ready")
    bot.loop.create_task(bot_loop())


# Event for when a reaction is added
@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.user_id == bot.user.id:
        return
    session = Session()
    reactions = db.Reaction.get_reaction_by_message_id(
        session, payload.message_id)
    if len(reactions) == 0 or reactions == None:
        return
    for reaction in reactions:
        if str(reaction.emoji) == str(payload.emoji):
            if reaction.expires != None:
                if reaction.expires < datetime.datetime.now():
                    return await bot.get_channel(payload.channel_id).send(embed=discord.Embed(title="Request expired", description="This request expired, please request again", color=discord.Color.red()))
            if reaction.action == ReactionActions.SIGNOFF:
                # Remove all data of the user
                # Get the user object
                session = Session()
                user = User.get_user_by_discord_id(session, payload.user_id)
                if user == None:
                    session.close()
                    return await bot.get_channel(payload.channel_id).send(embed=discord.Embed(title="Not authorized to do this", description="You are not athorized to perform this action", color=discord.Color.dark_red()))

                db.delete(session, user, commit=False)
                db.delete(session, reaction, commit=False)
                session.commit()
                session.close()
                return await bot.get_channel(payload.channel_id).send(embed=discord.Embed(title="You signed off", description="You signed off successfully, use !signup to sign back on!", color=discord.Color.magenta()))

    session.close()

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
    session = Session()
    user = db.User.get_user_by_discord_id(session, ctx.author.id)
    if user != None:
        embed = discord.Embed(title="You already have an account",
                              description=f"You have already signed up to the bot, do you wish to remove your old data and sign up again? Use the !signoff command", color=discord.Color.red())
        return await ctx.author.send(embed=embed)

    # TODO error handling
    client = Client(schoolname)
    auth = client.authenticate(token)
    access_token = auth["access_token"]
    usercode = client.get_user(access_token)[
        "response"]["data"][0]["code"]

    # Create database object
    user = db.User(discord_id=ctx.author.id, date_registered=datetime.date.today(
    ), zermelo_schoolname=schoolname, zermelo_access_token=access_token, zermelo_user_code=usercode, notify_before_start=15)

    db.insert(session, user)
    session.close()

    embed = discord.Embed(
        title="Success!", description=f"The bot retrieved your access token and created a user for you. You can change the notification settings with the !notifications command.", color=discord.Color.green())
    await ctx.author.send(embed=embed)
    client = None
    user = None
    logger.info("User signed up")
    return


# Get today's schedule
@bot.command(name="today", description="Get your schedule for today")
async def today(ctx: commands.Context, *args):
    """Command to get the schedule of today"""
    if ctx.message.guild:
        return await ctx.author.send(embed=discord.Embed(title="Error", description="Please only use the bot in private messages", color=discord.Color.dark_red()))

    # Get the user in the database
    session = Session()
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
    session = Session()
    user = db.User.get_user_by_discord_id(session, ctx.author.id)

    lessons = user.get_lessons(week)
    temp = [["" for _ in range(9)] for _ in range(5)]
    for lesson in lessons:
        weekday = datetime.datetime.utcfromtimestamp(lesson.start).weekday()
        hour = int(lesson.start_timeslot_name.split("u")[1])
        temp[weekday][hour - 1] = str(lesson)

    for i in range(5):
        header = [WEEKDAYS[i]]
        body = temp[i]
        tbody = [[body[j]] for j in range(len(body))]

        await ctx.send(f"```\n{t2a(header=header, body=tbody)}\n```")


# The signoff command
# Deletes all known data
@bot.command(name="signoff", description="Sign off and delete all data")
async def signoff(ctx: commands.Context, *args):
    session = Session()
    # Check if the user is signed up
    user = db.User.get_user_by_discord_id(session, ctx.author.id)
    if user == None:
        return await ctx.send(embed=discord.Embed(title="You are not signed up", description="You are not signed up to the bot so you cannot sign off either", color=discord.Color.dark_red()))

    signoff_message = await ctx.send(embed=discord.Embed(title="Sign off", description=f"Please sign off using the {NO} emoji, this request expires after 60 seconds", color=discord.Color.dark_red()))
    reaction = db.Reaction(message_id=signoff_message.id,
                           action=db.ReactionActions.SIGNOFF, emoji=NO, expires=datetime.datetime.now() + datetime.timedelta(minutes=1))
    db.insert(session, reaction)
    await signoff_message.add_reaction(NO)
    session.close()
    return
