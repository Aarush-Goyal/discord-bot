import discord
import os
import asyncio

import constants
from client import client
from discord.ext import tasks
from utils import get_seconds_till_weekday
from dotenv import load_dotenv

load_dotenv()


class GroupMeet:
    def __init__(self, client, channel_id):
        self.channel_id = channel_id  # os.environ['GBU_CHANNEL']
        self.client = client
        self.is_active = False
        self.reaction_message = None

        self.accepted_user_list = []
        self.rejected_user_list = []
        self.accepted_username_list = []
        self.rejected_username_list = []
        self.reactions = ["👍", "👎"]
        self.description = "Are you interested in this week's group meet?"
        self.prompt = self._get_basic_prompt()
        self._add_reaction_fields()

    def _get_basic_prompt(self):
        return discord.Embed(
            title='Group Meet ', description=self.description
        ).set_thumbnail(
            url='https://community.pepperdine.edu/it/images/googlemeetsmall.jpg'
        )

    def _add_reaction_fields(self):
        self.prompt.add_field(
            name="To accept the invite react with ", value="👍", inline=False)
        self.prompt.add_field(
            name="To reject the invite react with ", value="👎", inline=False)

    async def _add_reactions(self):
        for reaction in self.reactions:
            await self.reaction_message.add_reaction(reaction)

    async def send_message(self):
        self.reaction_message = await self.client.get_channel(
            int(self.channel_id)).send(embed=self.prompt)
        await self._add_reactions()
        self.is_active = True

    async def on_reaction(self, payload):
        if self.is_active and payload.message_id == self.reaction_message.id and payload.member.bot == False:
            # print(payload)
            if payload.emoji.name == "👍":
                print("added")
                if payload.user_id not in self.accepted_user_list:
                    self.accepted_user_list.append(payload.user_id)
                    self.accepted_username_list.append(payload.member.name)
                try:
                    self.rejected_user_list.remove(payload.user_id)
                    self.rejected_username_list.remove(payload.member.name)
                except:
                    pass

            elif payload.emoji.name == "👎":
                print("removed")
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

    async def add_users_to_db(self):
        pass

    async def post_groups_to_channel(self):

        getMentionStr = lambda x: f"<@{str(x)}>"
        getAssignedGroupPromptDescription = lambda \
            grp: f"**Group Lead**: {getMentionStr(grp[0])}\n" + "**Members**: " + " ".join(
            list(map(getMentionStr, grp)))
        groups = [[
            234395307759108106, 235148962103951360, 270904126974590976,
            349920059549941761
        ],
            [
                364012500682932234, 437808476106784770,
                475744554910351370, 751440083810385930
            ],
            [
                751441607043317771, 759093668841259018,
                773604743293173770, 785888095111086122
            ],
            [
                797880775051051048, 798037393739087872,
                798089922807988235, 798205111578263562
            ],
            [
                798238857178382379, 798244797575856150,
                798421601560952862, 798493698219442286,
                799185187900096532
            ]]

        prompt = discord.Embed(
            title='Assigned Groups',
            description=
            "Pls, find your respected groups for this week's Group Meeting"
        ).set_thumbnail(
            url=
            'https://lh3.googleusercontent.com/proxy/FvYtnlrHTrrcmQiZuvp3lLqyODoJdEzi2-j_TBUVssLXgzaLRHmFQ8ZvxDSIvT3brHbU4qA0NBC2hW7zCnjNiG5BlAaLhJKtBJpeWdHZmKM'
        )
        for idx, grp in enumerate(groups):
            prompt.add_field(
                name=
                f"-------------------'Group-{str(idx + 1).zfill(2)}'-------------------",
                value=getAssignedGroupPromptDescription(grp),
                inline=False)

        await self.client.get_channel(int(self.channel_id)).send(embed=prompt)


gm = GroupMeet(client=client, channel_id=int(os.getenv('GROUPMEET_CHANNEL')))


# GM_POLL
@tasks.loop(hours=168.0)
async def called_once_a_week_gm_poll():
    global gm
    await gm.send_message()


@called_once_a_week_gm_poll.before_loop
async def before_gm():
    await client.wait_until_ready()
    seconds_left = get_seconds_till_weekday(constants.GROUPMEET_POLL_WEEKDAY,
                                            constants.GROUPMEET_POLL_TIME)
    await asyncio.sleep(seconds_left)


# GM_ASSIGN
@tasks.loop(hours=168.0)
async def called_once_a_week_gm_assign():
    global gm
    if gm.accepted_user_list:
        await gm.add_users_to_db()
        await gm.post_groups_to_channel()
    gm = GroupMeet(
        client=client, channel_id=int(os.getenv('GROUPMEET_CHANNEL')))


@called_once_a_week_gm_assign.before_loop
async def before():
    await client.wait_until_ready()
    seconds_left = get_seconds_till_weekday(
        constants.GROUPMEET_GROUP_ASSIGN_WEEKDAY,
        constants.GROUPMEET_GROUP_ASSIGN_TIME)
    await asyncio.sleep(seconds_left)
