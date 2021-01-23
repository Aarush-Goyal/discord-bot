import discord
import re
import os
import asyncio
import requests
from client import client
from dotenv import load_dotenv
load_dotenv()


async def calc_days(message):
    tmp = message.content.split(" ")
    if len(tmp)>1:
        days = tmp[1]
    else:
        days = 7
    return days


async def get_report_from_db(message, days):
    url = os.getenv('BASE_URL') + '/api/v1/users/report?discord_id=' + str(message.author.id) + '&days=' + str(days) 
    headers = {
        'Content-Type': 'application/vnd.api+json'
    }

    resp = requests.request("GET", url, headers=headers)
    resp = resp.json()
    return resp


def get_prompt_report(days):
    return discord.Embed(
          title= 'Your report for last ' + str(days) + ' days'
        ).set_thumbnail(
            url = 'https://images.discordapp.net/avatars/535595120175611915/004416b242f631c5052ed81c3ddaad0d.png?size=512'
        )


async def show_user_report(resp, message, days):
    prompt = get_prompt_report(days)
    prompt.add_field(
        name="\nTotal questions solved:", value= str(resp["total_solved_ques"]), inline=False)

    prompt.add_field(
        name="Total number of questions:", value= str(resp["total_ques"]), inline=False)

    resp.pop("total_ques")
    resp.pop("total_solved_ques")
    report = ""


    if len(resp)>0:
      for topic,cnt in resp.items():
        report+= "\n" + topic + ": " + str(cnt)

    prompt.add_field(name="Question solved per topic: ", value= report,inline=False)

    await message.channel.send(embed= prompt)