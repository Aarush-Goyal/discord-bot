# Work with Python 3.6
import os
from services.gbu import called_once_a_week_gbu
from client import client
from event import on_user_message
from services.user import new_member_joined
from services.mmt import assign_mentor_to_new_user
from services import GroupMeet
from services.group import called_once_a_week_gm_poll, called_once_a_week_gm_assign
from dotenv import load_dotenv
#import asyncio



load_dotenv()
gm = GroupMeet(client=client,channel_id=int(os.getenv('GROUPMEET_CHANNEL')))

@client.event
async def on_ready():
    print('Logged in as', client.user.name, client.user.id)
    print('------')
    await gm.send_message()


@client.event
async def on_member_join(member):
    resp = await new_member_joined(member, int(os.getenv('GREETING_CHANNEL')))
    
    await assign_mentor_to_new_user(resp)


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    await on_user_message(message)
    

@client.event
async def on_raw_reaction_add(payload):
    if payload.channel_id == int(os.getenv('GROUPMEET_CHANNEL')):
        await gm.on_reaction(payload)




#CRONs
called_once_a_week_gbu.start()
called_once_a_week_gm_poll.start()
called_once_a_week_gm_assign.start()

#BOT
client.run(os.getenv('TOKEN'))