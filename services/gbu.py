import discord
import asyncio
from client import client

async def get_user_gbu(message_channel, member):
    prompt = discord.Embed(
        title='Welcome', description='Please enter your good')

    await member.send(embed=prompt)

    try:
        def check(message):
          return message.channel==member.dm_channel and message.author==member

        good = await client.wait_for("message",check=check, timeout=518400000)
        if good:
            await member.send('your recieved gbu : {0}'.format(good.content))

    except asyncio.TimeoutError:
        await member.send(
            'Sorry, your time limit to fill gbu has been extended.')
        good = False

    prompt = discord.Embed(
        title='Welcome', description='Please enter your BAD')

    await member.send(embed=prompt)

    try:
        def check(message):
          return message.channel==member.dm_channel and message.author==member
        
        bad = await client.wait_for("message",check=check, timeout=30000)
        if bad:
            await member.send('your recieved bad : {0}'.format(
                bad.content))

    except asyncio.TimeoutError:
        await member.send(
            'Sorry, your time limit to fill gbu has been extended.'
        )
        bad = False

    prompt = discord.Embed(
        title='Welcome', description='Please enter your UGLY')

    await member.send(embed=prompt)

    try:
        def check(message):
          return message.channel==member.dm_channel and message.author==member

        ugly = await client.wait_for("message",check=check, timeout=30000)
        if ugly:
            await member.send('your recieved ugly : {0}'.format(
                ugly.content))

    except asyncio.TimeoutError:
        await member.send(
            'Sorry, your time limit to fill gbu has been extended.'
        )
        ugly = False

    if good and bad and ugly:
      msg = '{0.mention}'.format(member) + ' has entered the GBU for this week: \n' + 'GOOD:' + good.content + '\nBAD: ' + bad.content + '\nUGLY: ' + ugly.content
      await message_channel.send(msg)
      print('sending')
