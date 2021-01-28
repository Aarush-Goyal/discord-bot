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
        'Content-Type': 'application/vnd.api+json',
        'Authorization': 'Bearer '+ os.getenv('TOKEN')
    }

    resp = requests.request("GET", url, headers=headers)
    resp = resp.json()
    return resp


def get_prompt_report(days):
    return discord.Embed(
          title= 'YOUR REPORT FOR LAST ' + str(days) + ' DAYS'
        ).set_thumbnail(
            url = 'https://media4.giphy.com/media/3orieMyfgezWc93UOc/200.gif'
        )


async def show_user_report(resp, message, days):
    prompt = get_prompt_report(days)
    prompt.add_field(
        name="Total questions solved", value= str(resp["total_solved_ques"]), inline=False)

    prompt.add_field(
        name="Total number of questions:", value= str(resp["total_ques"]), inline=False)

    resp.pop("total_ques")
    resp.pop("total_solved_ques")
    report = ""


    if len(resp)>0:
      for topic,cnt in resp.items():
        report+= "\n" + '`' + topic.capitalize() + '`' + "  :  " + str(cnt)

    prompt.add_field(name="Question solved per topic: ", value= report,inline=False)

    await message.channel.send(embed= prompt)