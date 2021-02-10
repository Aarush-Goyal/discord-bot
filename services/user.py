import discord
import re
import os
import asyncio

import requests

from client import client
from dotenv import load_dotenv
from utils import get_seconds_till_weekday, send_request
from logger import errorLogger, infoLogger
load_dotenv()

# Send greeting msg to new user and post user details in DB
GREETING_CHANNEL= os.getenv('GREETING_CHANNEL')
def get_user_joined_prompt():
    return discord.Embed(
          title='Devsnest Community'
        ).set_thumbnail(
            url = 'https://miro.medium.com/max/1600/0*C-cPP9D2MIyeexAT.gif'
        )

# Send greeting msg to new user and post user details in DB
async def new_member_joined(member, GREETING_CHANNEL):
  ch = client.get_channel(GREETING_CHANNEL)

  new_user_message = "New member " + member.name + " has joined the channel. Please everyone welcome " + member.name

  user_prompt = get_user_joined_prompt()
  user_prompt.add_field(name=" Welcome ", value= new_user_message, inline=False)
  asyncio.ensure_future(ch.send(embed= user_prompt))

  user_email = "temp@gmail.com"         #temporarily
  resp = await submit_user_details(member, user_email)
  return resp


async def get_user_email_and_id(user):
    prompt = discord.Embed(
        title='Welcome new User', description='Please enter your Email ID')

    await user.send(embed=prompt)

    async def validate_email(email):
        email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        return re.search(email_regex, email.content)

    def check(message):
      return message.channel==user.dm_channel

    try:
        email = await client.wait_for("message", check=check ,timeout=60)
        if await validate_email(email):
            await user.send('your recieved email : {0}'.format(
                email.content))
        else:
            await user.send(
                'Email not valid , pls try again with `-dn-email` command')
            email=False

    except asyncio.TimeoutError:
        asyncio.ensure_future(user.send(
            'Sorry, You didn\'t replied in time, Please send `-email` again to get the prompt again.'
        ))
        email = False

    return email


# Post user details in database
async def submit_user_details(member,user_email=None):

    url = '/api/v1/users'
    print(url)
    myobj = {
        "data": {
          "attributes":{
            "email": str(member.id)+'gmail.com',
            "name": member.display_name,
            "discord_id": str(member.id),
            "username": member.name,
            "password": "1234",
            "buddy":0
          },
          "type":"users"
        }
    }
    try:
        resp = await send_request(method_type="POST", url=url, data=myobj)
        infoLogger.info('User request successfully sent')
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
        errorLogger.error('Error while registering the user to the database', e)
        return None

    return resp.json()
    
