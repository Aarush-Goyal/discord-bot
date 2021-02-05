import discord
import os
import asyncio
import requests
import constants
from client import client
from discord.ext import tasks

from logger import errorLogger, infoLogger
from utils import get_seconds_till_weekday, send_request, data_not_found
from dotenv import load_dotenv

load_dotenv()
is_active = True


class GroupMeet:
    def __init__(self, client, channel_id):
        self.channel_id = channel_id  # os.environ['GBU_CHANNEL']
        self.client = client
        self.reaction_message = None

        self.accepted_user_list = []
        self.rejected_user_list = []
        self.accepted_username_list = []
        self.rejected_username_list = []
        self.reactions = ["👍", "👎"]
        self.description = "Get ready to be the part of weekly group meet. This is a plattform where you can interact with your peers and get to know them better. Feel free to discuss about your aspirations and goal and start networking"
        self.prompt = self._get_basic_prompt()
        self._add_reaction_fields()

    def _get_basic_prompt(self):
        return discord.Embed(
            title='Group Meet ', description=self.description
        ).set_thumbnail(
            url='https://media.tenor.com/images/5155ecadbe64a1c5c13d363ed22ce84d/tenor.gif'
        )

    def _add_reaction_fields(self):
        self.prompt.add_field(
            name="To accept the invite react with ", value="👍", inline=False)
        self.prompt.add_field(
            name="To reject the invite react with ", value="👎", inline=False)

    async def _add_reactions(self):
        for reaction in self.reactions:
            asyncio.ensure_future(self.reaction_message.add_reaction(reaction))

    async def send_message(self):
        global is_active
        self.reaction_message = await self.client.get_channel(
            int(self.channel_id)).send(embed=self.prompt)
        await self._add_reactions()
        is_active = True

    async def on_reaction(self, payload):
        global is_active
        if is_active and payload.message_id == self.reaction_message.id and payload.member.bot == False:
            if payload.emoji.name == "👍":
                asyncio.ensure_future(self.add_users_to_db(payload.user_id, 1))
                if payload.user_id not in self.accepted_user_list:
                    self.accepted_user_list.append(payload.user_id)
                    self.accepted_username_list.append(payload.member.name)
                try:
                    self.rejected_user_list.remove(payload.user_id)
                    self.rejected_username_list.remove(payload.member.name)
                except:
                    pass

            elif payload.emoji.name == "👎":
                asyncio.ensure_future(self.add_users_to_db(payload.user_id, 0))
                if payload.user_id not in self.rejected_user_list:
                    self.rejected_user_list.append(payload.user_id)
                    self.rejected_username_list.append(payload.member.name)
                try:
                    self.accepted_user_list.remove(payload.user_id)
                    self.accepted_username_list.remove(payload.member.name)
                except:
                    pass

            self.prompt = self._get_basic_prompt()
            self.prompt.add_field(
                name="To accept the invite react with 👍",
                value="Accepted User List\n" + "\n".join(
                    self.accepted_username_list),
                inline=False)
            self.prompt.add_field(
                name="To reject the invite react with 👎",
                value="Rejected User List\n" + "\n".join(
                    self.rejected_username_list),
                inline=False)
            await self.reaction_message.clear_reactions()
            await self._add_reactions()
            await self.reaction_message.edit(embed=self.prompt)

    async def add_users_to_db(self, user_id, choice):

        payload = {
            "data": {
                "attributes": {
                    "discord_id": str(user_id),
                    "choice": choice
                }
            }
        }
        try:
            await send_request(method_type="POST", url="api/v1/groupcalls/", data=payload)
            infoLogger.info('User response for the groupcall has been recorded')
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
            errorLogger.error('Error while recording user response for groupcall', e)

    async def post_groups_to_channel(self):

        try:
            groups_list = await send_request(method_type="GET", url="api/v1/groupcalls")
            infoLogger.info('Groups received from database')
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
            errorLogger.error('Error while getting the groups', e)
            groups_list=None

        if groups_list is None:
            return

        groups_list= groups_list.json()

        if groups_list == [[]]:
            print(self.client.get_channel(int(self.channel_id)))
            asyncio.ensure_future(data_not_found(self.client.get_channel(int(self.channel_id)), "No one accepted the group invite this week !"))
            return 

        groups = {}
        for idx,data in enumerate(groups_list):
           # user_id, idx = data
            if idx not in groups:
                groups[idx] = []
            for user in data:
                groups[idx].append(int(user["discord_id"]))

        getMentionStr = lambda x: f"<@{str(x)}>"
        getAssignedGroupPromptDescription = lambda \
            grp: f"**Group Lead**: {getMentionStr(grp[0])}\n" + "**Members**: " + " ".join(
            list(map(getMentionStr, grp)))


        prompt = discord.Embed(
            title='Group Meet Assigned Groups',
            description=
            "Pls, find your respected groups for this week's Group Meeting. \n \n The group meeting is scheduled at 9 pm tonight. Group leaders are required to moderate it."
        ).set_thumbnail(
            url='https://media1.giphy.com/media/VEhMiI26CCXVK6mixx/giphy.gif'
        )
        for idx, grp in enumerate(groups.values()):
            prompt.add_field(
                name=
                f"-------------------'Group-{str(idx + 1).zfill(2)}'-------------------\n \n",
                value=getAssignedGroupPromptDescription(grp),
                inline=False)

        asyncio.ensure_future(self.client.get_channel(int(self.channel_id)).send(embed=prompt))


gm = GroupMeet(client=client, channel_id=int(os.getenv('GROUPMEET_CHANNEL')))


# GM_POLL
@tasks.loop(hours=168.00)
async def called_once_a_week_gm_poll():
    global gm
    asyncio.ensure_future(gm.send_message())


@called_once_a_week_gm_poll.before_loop
async def before_gm():
    await client.wait_until_ready()
    seconds_left = get_seconds_till_weekday(constants.GROUPMEET_POLL_WEEKDAY,
                                            constants.GROUPMEET_POLL_TIME)                                     
    await asyncio.sleep(seconds_left)
    


# GM_ASSIGN
@tasks.loop(hours=168.00)
async def called_once_a_week_gm_assign():
    global gm, is_active
    await gm.post_groups_to_channel()
    gm = GroupMeet(
        client=client, channel_id=int(os.getenv('GROUPMEET_CHANNEL')))
    is_active=False

@called_once_a_week_gm_assign.before_loop
async def before():
    await client.wait_until_ready()
    seconds_left = get_seconds_till_weekday(
        constants.GROUPMEET_GROUP_ASSIGN_WEEKDAY,
        constants.GROUPMEET_GROUP_ASSIGN_TIME)   
    await asyncio.sleep(seconds_left)