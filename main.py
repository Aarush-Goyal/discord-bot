# Work with Python 3.6
import os
import asyncio

from logger import infoLogger, errorLogger
from services.gbu import called_once_a_week_gbu
from client import client
from event import on_user_message
from services.user import new_member_joined
from services.mmt import assign_mentor_to_new_user, called_once_a_week_mmt
from services.group import called_once_a_week_gm_poll, called_once_a_week_gm_assign, is_active, gm
from dotenv import load_dotenv

from listMembers import listExixtingMembers


load_dotenv()

@client.event
async def on_ready():
    print('Logged in as', client.user.name, client.user.id)
    print('------')
    await listExixtingMembers()


@client.event
async def on_member_join(member):
    resp = await new_member_joined(member, int(os.getenv('GREETING_CHANNEL')))
    if resp: 
        asyncio.ensure_future(assign_mentor_to_new_user(resp))
        infoLogger.info('Mentor assigned the the new user')
    else:
        errorLogger.error('Error while assigning mentor to the particular user')


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    asyncio.ensure_future(on_user_message(message))
    

@client.event
async def on_raw_reaction_add(payload):

    if payload.channel_id == int(os.getenv('GROUPMEET_CHANNEL')):
        from services.group import gm, is_active
        if is_active:
            await gm.on_reaction(payload)




#CRONs
called_once_a_week_gbu.start()
called_once_a_week_gm_poll.start()
called_once_a_week_gm_assign.start()
called_once_a_week_mmt.start()

#BOT
print("Discord bot started successfully")
print("New Image")
client.run(os.getenv('BOT_TOKEN'))
