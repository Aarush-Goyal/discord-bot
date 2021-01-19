import discord
import re
import os
import asyncio
import requests

from client import client

# Send greeting msg to new user and post user details in DB
async def new_member_joined(member, GREETING_CHANNEL):
  ch = client.get_channel(GREETING_CHANNEL)

  new_user_message = "New member " + member.name + " has joined the channel."
  await ch.send(new_user_message)

  user_email = await get_user_email_and_id(member)
  if user_email:
    resp = await submit_user_details(user_email,member)
  
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
                'Email not valid , pls try again with `-email` command')
            email=False

    except asyncio.TimeoutError:
        await user.send(
            'Sorry, You didn\'t replied in time, Please send `-email` again to get the prompt again.'
        )
        email = False

    return email


# Post user details in database
async def submit_user_details(user_email, member):

    url = os.environ['BASE_URL'] + '/api/v1/users'
    headers = {
        'Content-Type': 'application/vnd.api+json'
    }
    myobj = {
        "data": {
          "attributes":{
            "email": str(member.id)+ "@gmail.com",
            "name": "discord"+member.name,
            "discord_id": str(member.id),
            "username": member.name,
            "password": "1234",
            "buddy":0
          },
          "type":"users"
        }
    }

    resp = requests.request("POST", url, headers=headers, json=myobj)
    resp = resp.json()