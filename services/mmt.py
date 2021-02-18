import asyncio

import discord
from discord.ext import tasks
from dotenv import load_dotenv

import constants
from client import client
from logger import errorLogger, infoLogger
from utils import get_seconds_till_weekday, send_request

load_dotenv()


def get_basic_prompt(desc):
    return discord.Embed(
        title="Let us learn together",
        description=desc,
    ).set_thumbnail(
        url=(
            "https://onestop.utexas.edu/wp-content/uploads/"
            "2020/03/HelpWhenYouNeedIt.gif"
        )
    )


async def assign_mentors_to_all():
    resp = await send_request(method_type="GET", url="/api/v1/mmts")
    resp = resp.json()
    mentors_data = resp["data"]

    tasks = []
    for i in range(len(mentors_data)):
        attrs = mentors_data[i]["attributes"]
        user_discord_id = int(attrs["user_discord_id"])
        mentor_discord_id = int(attrs["mentors_discord_id"])

        user = await client.fetch_user(user_discord_id)
        mentor = await client.fetch_user(mentor_discord_id)

        user_msg = (
            f"Your new mentor is: {mentor.mention}.\n"
            "Feel free to schedule sessions weekly along with "
            "the mentor and get your doubts resolved weekly."
        )
        mentor_msg = (
            f"Your new mentee is: {user.mention}\n"
            "You are required to give a dedicated amount of time "
            "to your mentee and help him to get his/her doubts resolved."
        )
        user_prompt = get_basic_prompt(user_msg)
        mentor_prompt = get_basic_prompt(mentor_msg)

        tasks.append(asyncio.create_task(user.send(embed=user_prompt)))
        tasks.append(asyncio.create_task(mentor.send(embed=mentor_prompt)))
    await asyncio.wait(tasks)


async def assign_mentor_to_new_user(resp):
    attrs = resp["data"]["attributes"]
    user_discord_id = int(attrs["discord_id"])
    mentor_discord_id = int(attrs["mentor_discord_id"])

    try:
        user = await client.fetch_user(user_discord_id)
        infoLogger.info("User id is successfully retrieved from the discord.")
    except Exception:
        errorLogger.error("Error while retrieving the user from the discord")
        return
    try:
        mentor = await client.fetch_user(int(mentor_discord_id))
        infoLogger.info("Mentor id is successfully retrieved from the discord")
    except Exception:
        errorLogger.error("Error while retrieving the mentor from the discord")
        return

    user_msg = (
        "Welcome to Devsnest community. "
        "This is a world of peer learning.\n"
        "You can use dn-help command to get access to various options "
        "and play with the bot and make your learning ahead fun.\n\n"
        "Here we follow a mentor-mentee system so that everyone has access "
        "to someone who can clear doubts. "
        f"Your initial mentor is: {mentor.mention}\n"
        "Feel free to schedule sessions weekly along with the mentor and "
        "get your doubts resolved weekly. Let the learning begin!👍 "
    )
    mentor_msg = (
        f"Hope you are having a great time!\n"
        f"New Member has joined the channel now. {user.mention}\n"
        "He is your mentee for this week. \n"
        "You are required to help him with the server and give a dedicated amount "
        "of time to your mentee and help user to get doubts resolved. "
        "Continue learning 👍 "
    )
    user_prompt = get_basic_prompt(user_msg)
    mentor_prompt = get_basic_prompt(mentor_msg)

    asyncio.ensure_future(user.send(embed=user_prompt))
    asyncio.ensure_future(mentor.send(embed=mentor_prompt))


@tasks.loop(hours=168.0)  # 168 hours in a week
async def called_once_a_week_mmt():
    await assign_mentors_to_all()


@called_once_a_week_mmt.before_loop
async def before():
    await client.wait_until_ready()
    seconds_left = get_seconds_till_weekday(constants.MMT_WEEKDAY, constants.MMT_TIME)
    await asyncio.sleep(seconds_left)
