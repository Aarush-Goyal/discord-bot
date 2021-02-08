import asyncio
import os
import re

import discord
import requests
from dotenv import load_dotenv

from client import client
from logger import errorLogger
from utils import data_not_found, get_seconds_till_weekday, send_request

load_dotenv()


async def calc_days(message):
    msg = message.content.split(" ")
    if len(msg) > 1:
        try:
            days = int
            (msg[1])
            if days < 1:
                raise Exception("Invalid no of days")
        except:
            asyncio.ensure_future(
                data_not_found(message.channel, "Please enter valid no. of day count")
            )
            return False
    else:
        days = 7
    return days


async def get_report_from_db(message, days):
    url = (
        "/api/v1/users/report?discord_id="
        + str(message.author.id)
        + "&days="
        + str(days)
    )
    try:
        resp = await send_request(method_type="GET", url=url)
        resp = resp.json()
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
        errorLogger.error("Error while getting the report from the server", e)
        resp = None

    return resp


def get_prompt_report(days):
    return discord.Embed(
        title="YOUR REPORT FOR LAST " + str(days) + " DAYS"
    ).set_thumbnail(url="https://media4.giphy.com/media/3orieMyfgezWc93UOc/200.gif")


async def show_user_report(resp, message, days):
    ch = message.channel
    if not resp:
        asyncio.ensure_future(data_not_found(ch, "No Submissions Present !"))
        errorLogger.error("The report request failed with an empty response")
        return
    prompt = get_prompt_report(days)
    prompt.add_field(
        name="Total questions solved",
        value=str(resp["total_solved_ques"]),
        inline=False,
    )

    prompt.add_field(
        name="Total number of questions:", value=str(resp["total_ques"]), inline=False
    )

    resp.pop("total_ques")
    resp.pop("total_solved_ques")
    report = ""

    if len(resp) > 0:
        for topic, cnt in resp.items():
            report += "\n" + "`" + topic.capitalize() + "`" + "  :  " + str(cnt)

        prompt.add_field(name="Question solved per topic: ", value=report, inline=False)

    asyncio.ensure_future(message.channel.send(embed=prompt))
