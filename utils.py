
import datetime
from datetime import date
import pytz
import discord
import asyncio
from client import client
import requests
import os
from dotenv import load_dotenv
load_dotenv()

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
            'Sorry, You didn\'t reply on time.'
        )
        user_input = False
    
    return user_input


async def data_not_found(ch, title="Sorry, Invalid input has been passed"):
    embed=discord.Embed(
      title= title,
      description= 'You can use `dn-help` to get detail of commands'
    )
    await ch.send(embed=embed)


async def not_recognized(user,correct_command):
    embed=discord.Embed(
      title='Sorry, couldn\'t recognize that command.',
      description='Please use `'+correct_command+'` to start again.'
    )
    await user.send(embed=embed)


async def send_request(method_type, url, data=None):
    url = os.getenv('BASE_URL') + url

    headers = {
        'Content-Type': 'application/vnd.api+json',
        'Authorization': 'Bearer '+ os.getenv('TOKEN')
    }
   
    response = requests.request(method_type, url, headers=headers, json=data)
    print(response.json())
    return response
