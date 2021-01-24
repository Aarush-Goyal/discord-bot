
import datetime
from datetime import date
import pytz
import discord
import asyncio
from client import client
import requests

# Timezone
BASE_URL = "http://localhost:3000/api/v1/"
IST = pytz.timezone('Asia/Kolkata')

# Index for Sunday
d = {
    'MONDAY': 0,
    'TUESDAY': 1,
    'WEDNESDAY': 2,
    'THURSDAY': 3,
    'FRIDAY': 4,
    'SATURDAY': 5,
    'SUNDAY': 6
}

# Pass time in format HH:MM:SS.MS

def get_seconds_till_weekday(weekday, time):

    curr = date.today().weekday()
    diff = d[weekday] - curr

    next_weekday = datetime.datetime.today() + datetime.timedelta(days=diff)

    new_date = datetime.datetime.strptime(
        str(next_weekday.date()) + ' ' + time, '%Y-%m-%d %H:%M:%S.%f')

    DIFF = new_date - datetime.datetime.now(IST).replace(tzinfo=None)

    total_seconds = DIFF.days * 24 * 60 * 60 + DIFF.seconds

    return total_seconds


async def take_input_dm(user):
    try:
        def check(message):
          return message.channel==user.dm_channel and message.author==user
        
        user_input=await client.wait_for('message',check=check,timeout=60)
        
    except asyncio.TimeoutError:
        await user.send(
            'Sorry, You didn\'t replied in time.'
        )
        user_input = False
    
    return user_input

async def not_recognized(user,correct_command):
    embed=discord.Embed(
      title='Sorry, couldn\'t recognize that command.',
      description='Please use `'+correct_command+'` to start again.'
    )
    await user.send(embed=embed)


async def send_request(method_type, url, headers, data=None):
    url = BASE_URL + url
    response = requests.request(method_type, url, headers=headers, json=data)
    return response
