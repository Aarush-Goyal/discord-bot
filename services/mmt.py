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
      ).set_thumbnail(
            url = 'https://onestop.utexas.edu/wp-content/uploads/2020/03/HelpWhenYouNeedIt.gif'
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

    user_msg = 'Your new mentor is: {0.mention}'.format(mentor) + '\n Feel free to schedule sessions weekly along with the mentor and get your doubts resolved weekly. '
    mentor_msg = 'Your new mentee is: {0.mention}'.format(user) + '\n You are required to give a dedicated amount of time to your mentee and help him to get his/her doubts resolved.'
    user_prompt = get_basic_prompt(user_msg)
    mentor_prompt = get_basic_prompt(mentor_msg)

    await user.send( embed= user_prompt)
    await mentor.send( embed= mentor_prompt)
    # await user.send(user_msg)
    # await mentor.send(mentor_msg)	



async def assign_mentor_to_new_user(resp):
  print(resp)
  user_discord_id = resp["data"]["attributes"]["discord_id"]
  mentor_discord_id = resp["data"]["attributes"]["mentor_discord_id"]
  

  user = await client.fetch_user(int(user_discord_id)) 
  mentor = await client.fetch_user(int(mentor_discord_id))

  user_msg = 'Welcome to Devsnest community. This is a world of peer learning. Your initial mentor is: {0.mention}'.format(mentor) + '\n Feel free to schedule sessions weekly along with the mentor and get your doubts resolved weekly. Let the learning begin!👍 '
  mentor_msg = 'Hope you are having a great time! \n New Member has joined the channel now. {0.mention}'.format(user) + '\n He is your mentee for this week. \n You are required to help him with the server and give a dedicated amount of time to your mentee and help user to get doubts resolved. Continue learning 👍 '
  user_prompt = get_basic_prompt(user_msg)
  mentor_prompt = get_basic_prompt(mentor_msg)

  await user.send( embed= user_prompt)
  await mentor.send( embed= mentor_prompt)

  # await user.send(user_msg)
  # await mentor.send(mentor_msg)

