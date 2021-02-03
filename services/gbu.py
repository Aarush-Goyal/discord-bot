import discord
import asyncio
import os
import constants
from discord.ext import tasks
from client import client
from utils import get_seconds_till_weekday

def show_GBN_prompt(name):
    return discord.Embed(
           title= name + "'s GBN for the week"
        ).set_thumbnail(
            url = 'https://www.pngfind.com/pngs/m/326-3261800_person-thinking-png-thinking-icon-transparent-png.png'
        )

def describe_gbn_prompt():
  return discord.Embed(
          title='Hey, it\'s Introspection Time!', description= 'Every week we try to analyze what went good or bad during week and also what is our future plan for the next week.'
        )

async def get_from_user(member, msg):
  prompt = discord.Embed(
    title= msg)

  await member.send(embed=prompt)

  try:
    def check(message):
      return message.channel==member.dm_channel and message.author==member

    res = await client.wait_for("message",check=check, timeout=518400000)
    if res:
      await member.send('You filled: {0}'.format(res.content))

  except asyncio.TimeoutError:
    await member.send(
      'Sorry, your time limit to fill gbn has been extended.')
    res = False
  return res


async def get_user_gbu(message_channel, member):
    tell_about_gbn_prompt = describe_gbn_prompt()
    await member.send(embed= tell_about_gbn_prompt) 

    good = await get_from_user(member, "So what happened good in previous week")
    bad = await get_from_user(member, "What happened bad in last week")
    plan = await get_from_user(member, "What is your plan for next week")

    if good and bad and plan:
      gbn_prompt = show_GBN_prompt(member.name)
      gbn_prompt.add_field(name="Good : ", value= good.content,inline=False)
      gbn_prompt.add_field(name="Bad : ", value= bad.content,inline=False)
      gbn_prompt.add_field(name="Plan for next week : ", value= plan.content,inline=False)

      await message_channel.send(embed= gbn_prompt)



@tasks.loop(hours=168.0)  # 168 hours in a week
async def called_once_a_week_gbu():
    message_channel = client.get_channel(int(os.environ['GBU_CHANNEL']))
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
    await asyncio.sleep(0)#seconds_left)
