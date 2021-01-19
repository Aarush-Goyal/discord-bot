import discord
import requests
import os
from client import client

async def assign_mentors_to_all(member):
  
  resp = requests.get(os.environ['BASE_URL'] + '/api/v1/mmts')
  resp = resp.json()
  mentors_data = resp["data"]
        
  for i in range(len(mentors_data)):
    user_discord_id = mentors_data[i]["attributes"]["user_discord_id"]
    mentor_discord_id = mentors_data[i]["attributes"]["mentors_discord_id"]
            
    user = await client.fetch_user(int(user_discord_id))
    mentor = await client.fetch_user(int(mentor_discord_id))

    user_msg = 'Your new mentor is: {0.mention}'.format(mentor)
    mentor_msg = 'Your new mentee is: {0.mention}'.format(user)
    await user.send(user_msg)
    await mentor.send(mentor_msg)	



async def assign_mentor_to_new_user(resp):
  user_discord_id = resp["data"]["attributes"]["discord_id"]
  mentor_discord_id = resp["data"]["attributes"]["mentor_discord_id"]

  user = await client.fetch_user(int(user_discord_id)) 
  mentor = await client.fetch_user(int(mentor_discord_id))

  user_msg = 'Your mentor is: {0.mention}'.format(mentor)
  mentor_msg = 'Your nmentee is: {0.mention}'.format(user)

  await user.send(user_msg)
  await mentor.send(mentor_msg)