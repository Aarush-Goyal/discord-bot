# Work with Python 3.6

import asyncio
import os
# from dotenv import load_dotenv

from client import client
from discord.ext import tasks
from utils import get_seconds_till_weekday,not_recognized
from services.user import get_user_email_and_id, submit_details
from services.content import fetch,mark_done, mark_undone, mark_doubt
from services import GroupMeet
from services.gbu import get_user_gbu
import requests


TOKEN = os.getenv('TOKEN')
GREETING_CHANNEL = os.getenv('GREETING_CHANNEL_ID')
GBU_CHANNEL = os.getenv('GBU_CHANNEL_ID')
GROUPMEET_CHANNEL = os.getenv('GROUPMEET_CHANNEL_ID')
MENTOR_CHANNEL = os.getenv('MENTOR_CHANNEL_ID')


GBU_TIME = "15:06:00.000"
GBU_WEEKDAY = "SUNDAY"

GROUPMEET_POLL_TIME = "09:00:00.000"
GROUPMEET_POLL_WEEKDAY = "TUESDAY"

GROUPMEET_GROUP_ASSIGN_TIME = "09:00:00.000"
GROUPMEET_GROUP_ASSIGN_WEEKDAY = "WEDNESDAY"


# load_dotenv()
gm = GroupMeet(client=client,channel_id=GROUPMEET_CHANNEL)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    
    # await gm.send_message()



@client.event
async def on_member_join(member):
    ch = client.get_channel(GREETING_CHANNEL)

    new_user_message = "New member " + member.name + " has joined the channel."
    print(member)

    await ch.send(new_user_message)

    user_email = await get_user_email_and_id(member)

    if user_email:
        await submit_details(user_email,member)
        print('sending')

    ch =  client.get_channel(MENTOR_CHANNEL)
    
    url = 'http://127.0.0.1:3000/api/v1/users'
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

    user_discord_id = resp["data"]["attributes"]["discord_id"]
    mentor_discord_id = resp["data"]["attributes"]["mentor_discord_id"]


    user = await client.fetch_user(int(user_discord_id)) 
    mentor = await client.fetch_user(int(mentor_discord_id))

    user_msg = 'Your mentor is: {0.mention}'.format(mentor)
    mentor_msg = 'Your nmentee is: {0.mention}'.format(user)

    await user.send(user_msg)
    await mentor.send(mentor_msg)


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    
    if message.content.startswith('-assign-mentors'):
        resp = requests.get('http://localhost:3000/api/v1/mmts')
        resp = resp.json()
        mentors_data = resp["data"]
        
        for i in range(len(mentors_data)):
            user_discord_id = mentors_data[i]["attributes"]["user_discord_id"]
            mentor_discord_id = mentors_data[i]["attributes"]["mentors_discord_id"]
            
            user = await client.fetch_user(int(user_discord_id))
            mentor = await client.fetch_user(int(mentor_discord_id))

            user_msg = 'Your new mentor is: {0.mention}'.format(mentor)
            mentor_msg = 'Your new mentee is: {0.mention}'.format(user)
            await user.send(user_msg)
            await mentor.send(mentor_msg)	


    if message.content.startswith('-hello'):
        msg = 'hello {0.author.mention}'.format(message)
        await message.channel.send(msg)

    if message.content.startswith('-gbu'):
        msg = 'FILL ur GBU'
        await message.author.send(msg)

    if message.content.startswith('-email'):
        user_email = await get_user_email_and_id(message.author)
        if user_email:
            await submit_details(user_email, message.author)
            print('sending')

    if message.content.startswith('-fetch'):
        response=await fetch(message.author,message)
        if not response:
            await not_recognized(message.author, '-fetch')
    
    
    if message.content.startswith('-done'):
        response=await mark_done(message.author,message)
        if not response:
            await not_recognized(message.author, '-fetch')

    
    if message.content.startswith('-undone'):
        response=await mark_undone(message.author,message)
        if not response:
            await not_recognized(message.author, '-fetch')

    
    if message.content.startswith('-doubt'):
        response=await mark_doubt(message.author,message)
        if not response:
            await not_recognized(message.author, '-fetch')

@client.event
async def on_raw_reaction_add(payload):
  if payload.channel_id == GROUPMEET_CHANNEL:  
    await gm.on_reaction(payload)



# @client.event
# async def on_member_leave(member):
#   print('all Channels')
#   for channel in client.get_all_channels():
#     print(channel)

#   ch =  client.get_channel(GREETING_CHANNEL)
#   print(ch)

#   newUserMessage = "Recognised that a member called " + member.name + " left"
#   await ch.send(newUserMessage)

GBU_TIME = "09:00:00.000"
GBU_WEEKDAY = "SUNDAY"


# GBU
@tasks.loop(hours=168.0)  # 168 hours in a week
async def called_once_a_week():
    message_channel = client.get_channel(GBU_CHANNEL)
    print(f"Got channel {message_channel}")
    # loop = asyncio.get_running_loop()
    # loop.close()
    tasks = []

    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(get_user_gbu(message_channel, member))
        for member in message_channel.members if member.bot == False
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

# Runs before the task(when the bot comes online) and schedule it for next sunday
@called_once_a_week.before_loop
async def before():
    await client.wait_until_ready()
    seconds_left = get_seconds_till_weekday(GBU_WEEKDAY, GBU_TIME)
    print(seconds_left)
    await asyncio.sleep(0)


# GM_POLL
@tasks.loop(hours=168.0)  # 168 hours in a week
async def called_once_a_week_gm_poll():
    global gm
    await gm.send_message()

@called_once_a_week_gm_poll.before_loop
async def before():
    await client.wait_until_ready()
    seconds_left = get_seconds_till_weekday(GROUPMEET_POLL_WEEKDAY, GROUPMEET_POLL_TIME)
    print(seconds_left)
    await asyncio.sleep(seconds_left)


# GM_ASSIGN
@tasks.loop(hours=168.0)  # 168 hours in a week
async def called_once_a_week_gm_assign():
    global gm
    if gm.accepted_user_list:
      await gm.add_users_to_db()
      await gm.post_groups_to_channel()
    gm = GroupMeet(client=client,channel_id=GROUPMEET_CHANNEL)

@called_once_a_week_gm_assign.before_loop
async def before():
    await client.wait_until_ready()
    seconds_left = get_seconds_till_weekday(GROUPMEET_GROUP_ASSIGN_WEEKDAY, GROUPMEET_GROUP_ASSIGN_TIME)
    print(seconds_left)
    await asyncio.sleep(seconds_left)

# Interview
# @tasks.loop(hours=5.0)
# async def called_once_a_week():
#     message_channel = client.get_channel(798256240818913300)
#     print(f"Got channel {message_channel}")
#     await message_channel.send("Ready for interview")



called_once_a_week.start()
called_once_a_week_gm_poll.start()
called_once_a_week_gm_assign.start()

client.run(TOKEN)