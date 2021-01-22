import discord
import requests
import os
from client import client
from utils import take_input_dm
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv('BASE_URL') + '/api/v1/contents'


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

        print(content)

    except:
        print('Cannot get curriculums')
        content = False
    return content


def embed_content(embed, content):
    embed.clear_fields()

    for i in range(len(content)):

        value = 'Use command ' + \
                '`' + "dn-fetch " + content[i]['unique_id'] + '`'

        if content[i]['link']:
            value = '[{0}]({0})'.format(content[i]['link'])

        embed.add_field(
            name='`' + content[i]['unique_id'] + '`' + content[i]['name'].capitalize(),
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


async def fetch_content(user, unique_id):
    res = requests.get(BASE_URL+'?filter[parent_id]=' + unique_id)

    print(BASE_URL + '?filter[parent_id]=' + unique_id)
    url = BASE_URL + '?filter[parent_id]=' + unique_id
    res = {}

    embed = discord.Embed(
        title='Resource',
        description='Welcome to the world of learning! Here is the list of questions for you to practice. Choose the resource by typing out the name. For example: If you wish to solve a question of array, type dn-fetch Arrays',
    )

    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()

    if not response.status_code == 200:
        return False
    else:
        content = extract_content(data)

        if not content:
            return False

        await prompt_and_check(user, embed, content, False)

    return True


async def fetch(user, command):
    command = command.content.split(' ')

    if len(command) > 1:
        return await fetch_content(user, command[1])

    embed = discord.Embed(
        title='Resource',
       description='Welcome to the world of learning! Here is the list of questions for you to practice. Choose the resource by typing out the name. For example: If you wish to solve a question of array, type dn-fetch Arrays',
    )

    payload = {}
    headers = {}

    # BASE_URL= 'http://127.0.0.1:3000/api/v1/contents'
    response = requests.request("GET", BASE_URL, headers=headers, data=payload)
    data = response.json()

    curriculums = extract_content(data)
    if not curriculums:
        return False

    user_input = await prompt_and_check(user, embed, curriculums)
    if not user_input:
        return False

    url = BASE_URL + '?filter[parent_id]=' + user_input.content
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()

    subtopics = extract_content(data)

    if not subtopics:
        return False

    user_input = await prompt_and_check(user, embed, subtopics)
    if not user_input:
        return False

    return True



async def send_done_in_channel(user, unique_id):

    # TODO Uncommnent
    res=requests.get(BASE_URL + '?filter[unique_id]=' + unique_id)

    try:
        question_name=res['data'][0]['attributes']['name']
        question_link=res['data'][0]['attributes']['link']
    except:
        return False
    
    embed = discord.Embed(
        title='Status Update',
        description='{0} has solved Question `{1}`'.format(
        user.mention, question_name)
    )

    embed.add_field(name="Question Link",value="You can also try it [here]({0})".format(question_link),inline=False)
    embed.add_field(name="Unique ID",value=("Question Unique ID : "+'`'+unique_id+'`'),inline=False)    
    
    confetti_png=str('https://www.kindpng.com/picc/m/555-5554493_confetti-emoji-hd-png-download.png')
    
    embed.set_thumbnail(url=confetti_png)
    
    ch = client.get_channel(int(os.getenv('GROUPMEET_CHANNEL')))

    await ch.send(embed=embed)


async def mark_ques_status(user, command, status):
    unique_id = command.content.split(' ')[1]
    res = await update_submissions(user, unique_id, status)

    if status == 0:
        desc = "Marked done"
    elif status == 1:
        desc = "Marked undone"
    elif status == 2:
        desc = "Marked doubt"

    embed = discord.Embed(
        title='Resource',
        description=desc,
    )

    if not res.status_code == 200:
        return False

    else:
        content = extract_content(res)
        if not content:
            await user.send(embed=embed)

            if status == 0:
                await send_done_in_channel(user, unique_id)

            return True

        await prompt_and_check(user, embed, content, False)


async def update_submissions(user, unique_id, status):
    id = user.id
    url = os.getenv('BASE_URL') + '/api/v1/submissions'
    headers = {
        'Content-Type': 'application/vnd.api+json'
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
    print(res.status_code)
    return res
