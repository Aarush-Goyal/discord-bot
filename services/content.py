import discord
import requests
import os
from client import client
from utils import take_input_dm, send_request
from dotenv import load_dotenv

load_dotenv()

def extract_content(sample):
    content = []
    try:
        for _content in sample['data']:
            temp = {}
            temp['name'] = _content['attributes']['name']
            temp['unique_id'] = _content['attributes']['unique_id']
            if not _content['attributes']['link'] == "null":
                temp['link'] = _content['attributes']['link']
            else:
                temp['link'] = None
            content.append(temp)

    except:
        #Cannot get curriculums
        content = False
    return content


def embed_content(embed, content):
    embed.clear_fields()

    for i in range(len(content)):

        value = 'Use command ' + \
                '`' + "dn-fetch " + content[i]['unique_id'].capitalize() + '`'

        if content[i]['link']:
            value = '[{0}]({0})'.format(content[i]['link'])

        if content[i]['name']:
            name='`' + content[i]['unique_id'].capitalize() + '`  ' + content[i]['name'].capitalize()
        else:
            name='`' + content[i]['unique_id'].capitalize() + '`'

        embed.add_field(
            name='`' + content[i]['unique_id'] +
            '`' + content[i]['name'].capitalize(),            
            value=value,
            inline=False,
        )
    return embed


async def prompt_and_check(user, embed, content, input=True):
    embed = embed_content(embed, content)
    await user.send(embed=embed)

    if input:
        user_input = await take_input_dm(user)

        if not user_input:
            return False

        valid = False
        for i in content:
            if user_input.content == i['unique_id']:
                valid = True
                break

        if not valid:
            user_input = False

    else:
        return True

    return user_input


async def fetch_content(unique_id, ch):
    url = os.getenv('BASE_URL') + '/api/v1/contents?filter[parent_id]=' + unique_id

    embed = discord.Embed(
        title= unique_id + ' Questions 💻',
        description='Let us solve some questions now. Here is a list of questions for you to solve. Reach out to these questions using below link. \n \n Once you start solving the question you can mark the status as done, undone or doubt using command dn-mark-[status] [Question no.]. \n \n For example if you want to mark Q1 as done enter command dn-mark-done Q1. \n Happy Learning 😀',
    )

    payload = {}
    headers = {
        'Authorization': 'Bearer '+ os.getenv('TOKEN'),
        'Host': os.getenv('HOST')
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()

    if not response.status_code == 200:
        return False
    else:
        content = extract_content(data)

        if not content:
            return False

        embed = embed_content(embed, content)
        await ch.send(embed=embed)

    return True


async def fetch(message):
    ch = message.channel
    command = message.content.split(' ')

    if len(command) > 1:
        return await fetch_content(command[1], ch)

    embed = discord.Embed(
        title='Topics 💻',
       description='Welcome to the world of learning! Here is the list of questions for you to practice. Choose the resource by typing out the name. \n \n For example: If you wish to solve a question of array, type dn-fetch Arrays \n \n',
    )

    payload = {}
    headers = {
        'Authorization': 'Bearer '+ os.getenv('TOKEN'),
        'Host': os.getenv('HOST')
    }

    response = requests.request("GET", os.getenv('BASE_URL') + '/api/v1/contents?filter[parent_id]=algo', headers=headers, data=payload)
    data = response.json()

    curriculums = extract_content(data)
    if not curriculums:
        return False

    embed = embed_content(embed, curriculums)
    await ch.send(embed=embed)

    return True


async def send_done_in_channel(user, unique_id):

    # TODO Uncommnent
    headers = {
        'Authorization': 'Bearer '+ os.getenv('TOKEN'),
        'Host': os.getenv('HOST')
    }
    
    res=requests.get( os.getenv('BASE_URL') + '/api/v1/contents?filter[unique_id]=' + unique_id, headers=headers)
    res=res.json()

    try:
        question_name = res['data'][0]['attributes']['name']
        question_link = res['data'][0]['attributes']['link']
    except:
        
        return False

    embed = discord.Embed(
        title='Status Update',
        description='{0} has solved Question `{1}`'.format(
            user.mention, question_name)
    )

    embed.add_field(name="You can too give it a shot now!", value="Try it [here]({0})".format(
        question_link), inline=False)
    # embed.add_field(name="Unique ID", value=(
    #     "Question Unique ID : "+'`'+unique_id+'`'), inline=False)

    confetti_png = str(
        'https://media1.tenor.com/images/ed2bcee37ffb2944ecafec3e852d6014/tenor.gif?itemid=10369910')

    embed.set_thumbnail(url=confetti_png)

    ch = client.get_channel(int(os.getenv('STATUS_CHANNEL')))

    await ch.send(embed=embed)


async def mark_ques_status(user, command, status):
    ch = command.channel
    unique_id=command.content.split(' ')[1]
    res = await update_submissions(user, unique_id, status)

    if status == 0:
        desc = "Congratulations‼ \n This question has been marked as done. Keep Going 😄"
    elif status == 1:
        desc = "Hey, This question has been marked as undone. Try solving it. All the best‼ 😎"
    elif status == 2:
        desc = "Seems like, you're Stuck‼ 😶 \n This question has been marked as doubt. \n Try solving, Incase you are not able to solve, feel free to contact your mentor. Let this not hinder your learning 👍 "
    embed = discord.Embed(
        title='Question status marked successfully 👍 ',
        description=desc,
    )

    if not res.status_code == 200:
        return False

    else:
        content = extract_content(res)
        if not content:
            await ch.send(embed=embed)

            if status == 0:
                await send_done_in_channel(user, unique_id)
            return True
        await prompt_and_check(user, embed, content, False)

async def update_submissions(user, unique_id, status):
    id = user.id
    url = os.getenv('BASE_URL') + '/api/v1/submissions'
    headers = {
        'Content-Type': 'application/vnd.api+json',
        'Authorization': 'Bearer '+ os.getenv('TOKEN'),
        'Host': os.getenv('HOST')
    }

    myobj = {
        "data": {
            "attributes": {
                "discord_id": id,
                "question_unique_id": unique_id,
                "status": status
            },
            "type": "submissions"
        }
    }
    # get response
    res = requests.request("POST", url, headers=headers, json=myobj)
   
    return res

def embed_leaderboard(embed, leaderboard):
    embed.clear_fields()

    for i in range(len(leaderboard)):

        name = leaderboard[i]['name'].capitalize()
        score = leaderboard[i]['score']
        if score==None:
            score='zero'

        embed.add_field(
            name=name,
            value='has solved {0} questions this week.'.format(score),
            inline=False,
        )

    return embed


async def get_leaderboard(message):
    headers = {'Content-Type': 'application/json',
        'Authorization': 'Bearer '+ os.getenv('TOKEN'),
        'Host': os.getenv('HOST')
    }
    url = os.getenv('BASE_URL')+'/api/v1/users/leaderboard'
    response = requests.request("GET", url, headers=headers)

    res = response.json()
    
    embed = discord.Embed(title='Leaderboard',description='Here are the top performers. Keep going👍')
    embed = embed_leaderboard(embed, res)
    
    leaderboard_png='https://thumbs.gfycat.com/EthicalPerfumedAsiaticwildass-size_restricted.gif'
    embed.set_thumbnail(url=leaderboard_png)
    
    await message.channel.send(embed=embed)
    return True

async def wrong_channel_prompt(desc):
  return discord.Embed(
        title='Oooooops! Seems like a Wrong channel :(',
        description= desc,
    ).set_thumbnail(
            url = 'https://media.tenor.com/images/2b454269146fcddfdae60d3013484f0f/tenor.gif'
        )


async def check_channel_ask_a_bot(message):
  ch = message.channel
  if ch.id != int(os.environ['ASK_A_BOT']) and type(ch).__name__ != 'DMChannel':
    prompt = await wrong_channel_prompt("Type this command in 'Ask-a-Bot channel' or DM the bot to get the desired result !! ")
    await ch.send(embed= prompt)
    return False
  else:
    return True