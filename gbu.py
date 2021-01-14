
# Work with Python 3.6
import discord
import requests
import asyncio
from discord.ext import tasks


TOKEN = 'Nzk5MTg1MTg3OTAwMDk2NTMy.X__5NA.2zw3QVg8-NHffidRthMH4TQ919I'

#MENTOR_CHANNEL = 799186069471100929
GBU_CHANNEL = 798486635800952832

intents = discord.Intents.all() # trigger events for all
client=discord.Client(intents=intents)

# welcomechannel = await client.fetch_channel(channel_id)

@client.event 
async def on_message(message):

    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
        
    if message.content.startswith('-gbu'):
        user_good, user_bad, user_ugly = await get_user_gbu(message.author)
        if user_good and user_bad and user_ugly:
            msg = '{0.author.mention}'.format(message) + ' has entered the GBU for this week: \n' + 'GOOD: ' + user_good.content + '\nBAD: ' + user_bad.content + '\nUGLY: ' + user_ugly.content
            await message.channel.send(msg)
            print('sending')    	
		


async def get_user_gbu(member):
    prompt = discord.Embed(
        title='Welcome', description='Please enter your GOOD')

    await member.send(embed=prompt)

    try:
        good = await client.wait_for("message", timeout=300)
        if good:
            await member.send('your recieved good : {0}'.format(
                good.content))

    except asyncio.TimeoutError:
        await member.send(
            'Sorry, You didn\'t replied in time, Please send `-gbu` again to get the prompt again.'
        )
        good = False

    prompt = discord.Embed(
        title='Welcome', description='Please enter your BAD')

    await member.send(embed=prompt)

    try:
        bad = await client.wait_for("message", timeout=300)
        if bad:
            await member.send('your recieved bad : {0}'.format(
                bad.content))

    except asyncio.TimeoutError:
        await member.send(
            'Sorry, You didn\'t replied in time, Please send `-gbu` again to get the prompt again.'
        )
        bad = False


    prompt = discord.Embed(
        title='Welcome', description='Please enter your UGLY')

    await member.send(embed=prompt)

    try:
        ugly = await client.wait_for("message", timeout=300)
        if ugly:
            await member.send('your recieved ugly : {0}'.format(
                ugly.content))

    except asyncio.TimeoutError:
        await member.send(
            'Sorry, You didn\'t replied in time, Please send `-gbu` again to get the prompt again.'
        )
        ugly = False

    return good, bad, ugly

@client.event
async def on_ready():
 
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)	
    print('------')
  
    
client.run(TOKEN)
