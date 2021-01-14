
# Work with Python 3.6
import discord
import requests
import asyncio
from discord.ext import tasks


TOKEN = 'Nzk5MTg1MTg3OTAwMDk2NTMy.X__5NA.2zw3QVg8-NHffidRthMH4TQ919I'

MENTOR_CHANNEL = 799186069471100929


intents = discord.Intents.all() # trigger events for all
client=discord.Client(intents=intents)

# welcomechannel = await client.fetch_channel(channel_id)

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
	    	await message.channel.send(mentors_data[i]["attributes"])
    	 
	
    if message.content.startswith('-assign-mentor-to-me'):
        response = requests.get('http://localhost:3000/api/v1/mmts/85')
        msg = 'details of your mentor for this week is '
        await message.channel.send(msg)
        await message.channel.send(response.json())   	


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)	
    print('------')
    
    

@client.event
async def on_member_join(member):
    ch =  client.get_channel(MENTOR_CHANNEL)
    print(ch)	

    requests.post('http://localhost:3000/signup',json={  
    "user": {
      "email": "eiieehiu@gmail.com",
      "password":"1234",
      "name":"priya mishra" 
      }
    })
    
    resp = requests.get('http://localhost:3000/api/v1/users/70')
    resp = resp.json()
    
    
    mentor_name = resp["data"]["attributes"]["mentor_name"]
        
    newUserMessage = 'Welcome {0.mention}'.format(member) 
    mentorTxt = " Your mentor is " + mentor_name
    menteeTxt = " Your mentee is " + member.name  
    
    await ch.send(newUserMessage)
    await member.send(mentorTxt)
    #msg mentor too
    
    
    
client.run(TOKEN)
