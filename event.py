from utils import not_recognized
from services.user import get_user_email_and_id, submit_user_details
from services.content import fetch, mark_ques_status
from services.mmt import assign_mentors_to_all
import discord
import os
from dotenv import load_dotenv
import requests


load_dotenv()

def get_prompt_help():
    return discord.Embed(
          title='DN Bot Guide', description= "Use these commands for smooth experience on the platform \n"
        ).set_thumbnail(
            url = 'https://cdn.wayscript.com/blog_img/83/DiscordBotThumb.png'
        )

def get_prompt_report():
    return discord.Embed(
          title='DN User Report'
        ).set_thumbnail(
            url = 'https://images.discordapp.net/avatars/535595120175611915/004416b242f631c5052ed81c3ddaad0d.png?size=512'
        )
        

async def on_user_message(message):
  if message.content.startswith('dn-assign-mentors'):
    await assign_mentors_to_all(message)

  if message.content.startswith('dn-hello'):
        msg = 'hello {0.author.mention}'.format(message)
        await message.channel.send(msg)
  

  if message.content.startswith('dn-help'):
        msg =  'dn-help: To get command help \n dn-ask: To contact moderators \n dn-fetch: To get list of questions \n dn-done: To mark question done \n dn-undone: To mark question undone \n dn-doubt: To get mark question as doubt \n dn-report: To get progress report \n dn-leaderboard: To get list of top 10 students of week \n '

        prompt = get_prompt_help()
        prompt.add_field(
                name="Here is your ultimate guide to DN bot.\n",
                value= msg,
                inline=False)

        await message.channel.send(embed= prompt)
        

  if message.content.startswith('dn-email'):
    user_email = await get_user_email_and_id(message.author)
    if user_email:
        await submit_user_details(user_email, message.author)
        print('sending')

  if message.content.startswith('dn-fetch'):
    response=await fetch(message.author,message)
    if not response:
      await not_recognized(message.author, 'dn-fetch')
    
    
  if message.content.startswith('dn-done'):
    response=await mark_ques_status(message.author,message, 1)
    if not response:
      await not_recognized(message.author, 'dn-fetch')

    
  if message.content.startswith('dn-undone'):
    response=await mark_ques_status(message.author,message, 0)
    if not response:
      await not_recognized(message.author, 'dn-fetch')

  if message.content.startswith('dn-doubt'):
    response=await mark_ques_status(message.author,message, 2)
    if not response:
        await not_recognized(message.author, 'dn-fetch')

  if message.content.startswith('dn-report'):
    url = os.getenv('BASE_URL') + '/api/v1/users/report?discord_id=' + str(message.author.id) + '&days=7' 
    headers = {
        'Content-Type': 'application/vnd.api+json'
    }

    resp = requests.request("GET", url, headers=headers)
    resp = resp.json()

    prompt = get_prompt_report()
    prompt.add_field(
        name="\nTotal questions solved:", value= str(resp["total_solved_ques"]), inline=False)

    prompt.add_field(
        name="Total ques:", value= str(resp["total_ques"]), inline=False)

    resp.pop("total_ques")
    resp.pop("total_solved_ques")
    report = ""


    if len(resp)>0:
      for topic,cnt in resp.items():
        report+= "\n" + topic + ": " + str(cnt)

    prompt.add_field(name="Topics: ", value= report,inline=False)

    await message.channel.send(embed= prompt)



