import discord
import requests
import os
from client import client
from dotenv import load_dotenv
import discord
load_dotenv()

def get_basic_prompt(desc):
    return discord.Embed(
        title='Let us learn together', description= desc
      )


async def assign_mentors_to_all(member):
  
  resp = requests.get(os.getenv('BASE_URL') + '/api/v1/mmts')
  resp = resp.json()
  mentors_data = resp["data"]
        
  for i in range(len(mentors_data)):
    user_discord_id = mentors_data[i]["attributes"]["user_discord_id"]
    mentor_discord_id = mentors_data[i]["attributes"]["mentors_discord_id"]
            
    user = await client.fetch_user(int(user_discord_id))
    mentor = await client.fetch_user(int(mentor_discord_id))

    user_msg = 'Your new mentor is: {0.mention}'.format(mentor)
    mentor_msg = 'Your new mentee is: {0.mention}'.format(user)
    user_prompt = get_basic_prompt(user_msg)
    mentor_prompt = get_basic_prompt(mentor_msg)

    await user.send( embed= user_prompt)
    await user.send( embed= mentor_prompt)
    # await user.send(user_msg)
    # await mentor.send(mentor_msg)	



async def assign_mentor_to_new_user(resp):
  user_discord_id = resp["data"]["attributes"]["discord_id"]
  mentor_discord_id = resp["data"]["attributes"]["mentor_discord_id"]

  user = await client.fetch_user(int(user_discord_id)) 
  mentor = await client.fetch_user(int(mentor_discord_id))

  user_msg = 'Your mentor is: {0.mention}'.format(mentor)
  mentor_msg = 'Your nmentee is: {0.mention}'.format(user)
  user_prompt = get_basic_prompt(user_msg)
  mentor_prompt = get_basic_prompt(mentor_msg)

  await user.send( embed= user_prompt)
  await user.send( embed= mentor_prompt)

  # await user.send(user_msg)
  # await mentor.send(mentor_msg)

