import os
import json
import time
from dotenv import load_dotenv
from datetime import datetime, timedelta

import discord
from discord.ext import commands, tasks

# Local imports
import db
import forms

load_dotenv()
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


def is_24hours_past():
    timestamp = db.get_last_update()
    given_timestamp = datetime.fromtimestamp(timestamp)
    current_time = datetime.now()
    time_difference = current_time - given_timestamp

    if time_difference <= timedelta(hours=24):
        print(time_difference)
        return False
    else:
        new_timestamp = time.time()
        db.set_last_update(new_timestamp)
        return True


def is_auth(user_id):
        user_ids = db.get_users_ids()
        if user_id in user_ids:
            return True
        else:
            return False


async def holidays_today():
    today = datetime.now().strftime("%d%m%Y")
    events = db.get_holiday(today)
    holidays = '\n'.join(f" - {event.title()} :partying_face:" for event in events)

    await send(holidays)


async def check_brth():
    # $discord_id $name $desc $birh
    users = db.list_users()
    current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    current_year = current_date.year

    for user in users:
        discord_id = user[0]
        name = user[1]
        brth = user[3]
        birth_date = datetime.strptime(brth, "%d%m%Y")
        birthday_this_year = birth_date.replace(year=current_year)

        # If the birthday for this year has passed, calculate for the next year
        if birthday_this_year < current_date:
            birthday_this_year = birthday_this_year.replace(year=current_year + 1)

        age = birthday_this_year.year - birth_date.year
        remaining_days = (birthday_this_year - current_date).days

        if remaining_days == 30 or remaining_days == 7:
            days_left = f"{remaining_days} days remaining until {name}'s birthday on {birthday_this_year.strftime('%d %b')}. They will turn {age} years old."
            how_to = f"Don't fortget to prepare your congratulations with !gc command in bot's DM\n Use !mygc to verify all your congratulations."
            warn_msg = f"{days_left}\n{how_to}"
            await send(warn_msg)

        elif remaining_days == 0:
            pretty_gc_msg = f"@everyone\nToday is <@{discord_id}>'s ({name}) birthday! 🎉 They are now {age} years old.\n"
            for sender_name, gc in db.get_gcs(discord_id):
                pretty_gc_msg += f"{sender_name} wrote:\n{gc}\n\n"
            await send(pretty_gc_msg)


async def send(message: str):
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(message)
    else:
        print("Channel not found!")


@bot.command()
async def gc(ctx):
    user_id = ctx.author.id
    if is_auth(user_id):
        await ctx.send(view=forms.CongratulationView())


@bot.command()
async def mygc(ctx):
    user_id = ctx.author.id
    if is_auth(user_id):
        gcs = db.get_self_gcs(user_id)
        reply_gen = (f"**{gc[0]}**:\n{gc[1]}\n" for gc in gcs)
        reply = '\n'.join(reply_gen)

        await ctx.send(reply)


@tasks.loop(seconds=86400)
async def bg_task():
    await bot.wait_until_ready()
    if is_24hours_past():
        await holidays_today()
        await check_brth()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")
    #bg_task.start()


bot.run(BOT_TOKEN)
