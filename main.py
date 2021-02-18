# Work with Python 3.6
import asyncio
import os

from dotenv import load_dotenv

from client import client
from event import on_user_message
from logger import errorLogger, infoLogger
from services.content import on_leaderboard_reaction
from services.mmt import assign_mentor_to_new_user
from services.user import new_member_joined

load_dotenv()


@client.event
async def on_ready():
    print("Logged in as", client.user.name, client.user.id)
    print("------")
    # await listExistingMembers()


@client.event
async def on_member_join(member):
    resp = await new_member_joined(member, int(os.getenv("GREETING_CHANNEL")))
    if resp:
        asyncio.ensure_future(assign_mentor_to_new_user(resp))
        infoLogger.info("Mentor assigned the the new user")
    else:
        errorLogger.error("Error while assigning mentor to the particular user")


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    asyncio.ensure_future(on_user_message(message))


@client.event
async def on_raw_reaction_add(payload):

    if payload.channel_id == int(os.getenv("GROUPMEET_CHANNEL")):
        from services.group import gm, is_active

        if is_active:
            await gm.on_reaction(payload)

    if payload.channel_id == int(os.getenv("ASK_A_BOT")):
        from event import last_leaderboard_message_id

        if payload.message_id == last_leaderboard_message_id:
            await on_leaderboard_reaction(payload)


# CRONs
# called_once_a_week_gbu.start()
# called_once_a_week_gm_poll.start()
# called_once_a_week_gm_assign.start()
# called_once_a_week_mmt.start()

# BOT
client.run(os.getenv("BOT_TOKEN"))
