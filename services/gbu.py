import discord
import asyncio
import os
import constants
from discord.ext import tasks
from client import client
from utils import get_seconds_till_weekday

def show_GBU_prompt(name):
    return discord.Embed(
          title= name + "'s GBU for the week"
        ).set_thumbnail(
            url = 'https://www.pngfind.com/pngs/m/326-3261800_person-thinking-png-thinking-icon-transparent-png.png'
        )


async def get_from_user(member, ques):
  prompt = discord.Embed(
    title="Hey, it's Introspection Time!", description='Tell us something ' + ques + ' about the week!')

  await member.send(embed=prompt)

  try:
    def check(message):
      return message.channel==member.dm_channel and message.author==member

    res = await client.wait_for("message",check=check, timeout=518400000)
    if res:
      await member.send('You filled: {0}'.format(res.content))

  except asyncio.TimeoutError:
    await member.send(
      'Sorry, your time limit to fill gbu has been extended.')
    res = False
  return res


async def get_user_gbu(message_channel, member):
    good = await get_from_user(member, "good")
    bad = await get_from_user(member, "bad")
    ugly = await get_from_user(member, "ugly")

    if good and bad and ugly:
      gbu_prompt = show_GBU_prompt(member.name)
      gbu_prompt.add_field(name="Good : ", value= good.content,inline=False)
      gbu_prompt.add_field(name="Bad : ", value= bad.content,inline=False)
      gbu_prompt.add_field(name="Ugly : ", value= ugly.content,inline=False)

      await message_channel.send(embed= gbu_prompt)
      print('sending')


@tasks.loop(hours=168.0)  # 168 hours in a week
async def called_once_a_week_gbu():
    message_channel = client.get_channel(int(os.environ['GBU_CHANNEL']))
    print(f"Got channel {message_channel}")
    tasks = []

    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(get_user_gbu(message_channel, member))
        for member in message_channel.members if member.bot == False
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

@called_once_a_week_gbu.before_loop
async def before_gbu():
    await client.wait_until_ready()
    seconds_left = get_seconds_till_weekday(constants.GBU_WEEKDAY, constants.GBU_TIME)
    await asyncio.sleep(seconds_left)
