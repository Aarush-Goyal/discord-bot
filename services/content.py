import discord
import requests

from logger import errorLogger, infoLogger
import os
from client import client
from utils import take_input_dm, send_request, data_not_found
from dotenv import load_dotenv

import asyncio

load_dotenv()
total_leaderboard_pages=100

def extract_content(sample):
    content = []
    try:
        for _content in sample['data']:
            temp = {'name': _content['attributes']['name'],
                    'unique_id': _content['attributes']['unique_id']}
            if not _content['attributes']['link'] == "null":
                temp['link'] = _content['attributes']['link']
            else:
                temp['link'] = None
            content.append(temp)

    except:
        # Cannot get curriculums
        errorLogger.error('Cannot get curriculums')
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
            name = '`' + content[i]['unique_id'].capitalize() + \
                '`  ' + content[i]['name'].capitalize()
        else:
            name = '`' + content[i]['unique_id'].capitalize() + '`'

        embed.add_field(
            # name='`' + content[i]['unique_id'] +
            # '`' +content[i]['name'].capitalize(),
            name=name,
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
    url = '/api/v1/contents?filter[parent_id]=' + unique_id

    embed = discord.Embed(
        title=unique_id + ' Questions 💻',
        description='Let us solve some questions now. Here is a list of questions for you to solve. Reach out to these questions using below link. \n \n Once you start solving the question you can mark the status as done, undone or doubt using command dn-mark-[status] [Question no.]. \n \n For example if you want to mark Q1 as done enter command dn-mark-done Q1. \n Happy Learning 😀',
    )

    payload = {}
    try:
        response = await send_request(method_type="GET", url=url, data=payload)
        infoLogger.info('Fetch request is successful')
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
        errorLogger.error('Error while getting response', exc_info=e)
        response = None

    if not response:
        asyncio.ensure_future(data_not_found(ch, "Invalid topic name!"))
        errorLogger.error('Content not found')
        return False

    resp = response.json()

    if len(resp["data"]) == 0:
        asyncio.ensure_future(data_not_found(ch, "Invalid topic name!"))
        errorLogger.error('The topic does not exist in the database')
        return False
    else:
        content = extract_content(resp)

        if not content:
            errorLogger.error('invalid content')
            return False

        embed = embed_content(embed, content)
        asyncio.ensure_future(ch.send(embed=embed))

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

    try:
        response = await send_request(method_type="GET", url='/api/v1/contents?filter[parent_id]=algo', data=payload)
        infoLogger.info('topics fetched')
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
        errorLogger.error('Error while getting the fetch response', exc_info=e)
        response = None

    if not response:
        asyncio.ensure_future(data_not_found(ch, "No topics present !"))
        errorLogger.error('The request failed with an empty response')
        return False

    resp = response.json()

    if len(resp["data"]) == 0:
        asyncio.ensure_future(data_not_found(ch, "No topics present !"))
        errorLogger.error('Fetch request failed with an empty data')
        return False

    curriculums = extract_content(resp)
    if not curriculums:
        asyncio.ensure_future(data_not_found(ch, "No topics present !"))
        errorLogger.error('No topics found while parsing curriculum')
        return False

    embed = embed_content(embed, curriculums)
    asyncio.ensure_future(ch.send(embed=embed))
    infoLogger.info('Fetch Data: Embed sent to the channel')

    return True


async def send_done_in_channel(user, unique_id):
    ch = client.get_channel(int(os.getenv('STATUS_CHANNEL')))

    url = '/api/v1/contents?filter[unique_id]=' + unique_id
    res = await send_request(method_type="GET", url=url)
    res = res.json()

    # Error in sending data to channel
    # if len(res["data"])==0:

    try:
        question_name = res['data'][0]['attributes']['name']
        question_link = res['data'][0]['attributes']['link']
        infoLogger.info('update-submissions: data successfully parsed')
    except:
        errorLogger.error('Error while parsing data')
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

    asyncio.ensure_future(ch.send(embed=embed))
    infoLogger.info('Question Status: Embed sent to the channel')


async def mark_ques_status(user, command, status):
    ch = command.channel
    try:
        unique_id = command.content.split(' ')[1]
        infoLogger.info('Question unique id is received')
    except IndexError as e:
        errorLogger.error(
            'No unique_id is received from the command', exc_info=e)
        asyncio.ensure_future(data_not_found(
            ch, "No question id is mentioned, Please enter correct one!"))
        return
    res = await update_submissions(user, unique_id, status)
    if not res:
        asyncio.ensure_future(data_not_found(
            ch, "Invalid question id, Please enter correct one!"))
        return res
    res = res.json()

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

    if not res["data"]["id"]:
        asyncio.ensure_future(data_not_found(
            ch, "Invalid question id, Please enter correct one!"))
        errorLogger.error('Invalid question id')

    else:
        content = extract_content(res)
        if not content:
            asyncio.ensure_future(ch.send(embed=embed))

            if status == 0:
                asyncio.ensure_future(send_done_in_channel(user, unique_id))
            return True
        asyncio.ensure_future(prompt_and_check(user, embed, content, False))


async def update_submissions(user, unique_id, status):
    id = user.id
    url = '/api/v1/submissions'

    payload = {
        "data": {
            "attributes": {
                "discord_id": id,
                "question_unique_id": unique_id,
                "status": status
            },
            "type": "submissions"
        }
    }
    try:
        response = await send_request(method_type="POST", url=url, data=payload)
        infoLogger.info('send_request: submissions updated successfully')
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
        errorLogger.error('Error while submitting the response', exc_info=e)
        response = None

    return response


def embed_leaderboard(embed, leaderboard):
    embed.clear_fields()
    
    for i in range(len(leaderboard)):

        name = leaderboard[i]['name'].capitalize()
        score = leaderboard[i]['score']
        if score == None:
            score = 'zero'

        embed.add_field(
            name=name,
            value='has solved {0} questions.'.format(score),
            inline=False,
        )

    return embed


async def add_leadeboard_reaction(message, reactions):
    await message.clear_reactions()
    for reaction in reactions:
        asyncio.ensure_future(message.add_reaction(reaction))


async def get_leaderboard_embed(url, message, page=1):
    reactions = ['🔼', '🔽']

    try:
        res = await send_request(method_type="GET", url=url+'?page='+str(page))
        infoLogger.info('leaderboard is successfully retrieved')
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
        errorLogger.error('Error while getting the leaderboard', exc_info=e)
        res = None

    if not res:
        asyncio.ensure_future(data_not_found(
            message.channel, "Insufficient data to create leaderboard !"))
        return False

    res = res.json()
    
    #** from res
    global total_leaderboard_pages
    total_pages = res['count']
    total_leaderboard_pages=total_pages
    

    embed = discord.Embed(
        title='Leaderboard', description='Here are the top performers. Keep going👍')
    embed = embed_leaderboard(embed, res['scoreboard'])

    leaderboard_png = 'https://thumbs.gfycat.com/EthicalPerfumedAsiaticwildass-size_restricted.gif'
    embed.set_thumbnail(url=leaderboard_png)

    embed.set_footer(text='Page : '+str(page)+'/'+str(total_pages))

    return embed


async def get_leaderboard(message,page):
    reactions = ['🔼', '🔽']
    url = 'api/v1/users/leaderboard'

    embed = await get_leaderboard_embed(url, message, page)
    message_sent = await message.channel.send(embed=embed)

    await add_leadeboard_reaction(message_sent, reactions)

    return message_sent.id


async def on_leaderboard_reaction(payload): 
    from event import current_leaderboard_page_number
    page = current_leaderboard_page_number
    
    reactions = ['🔼', '🔽']
    if payload.member.bot == False and reactions.__contains__(payload.emoji.name):
        url = 'api/v1/users/leaderboard'

        if payload.emoji.name == "🔽":
            page = page + 1

        if payload.emoji.name == "🔼":
            page = page - 1

        if page <= 0:
            page = 1
        
        if page > total_leaderboard_pages:
            page = total_leaderboard_pages

        from event import update_current_leaderboard_page_number
        update_current_leaderboard_page_number(page)
        

        channel = await client.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        embed = await get_leaderboard_embed(url, message, page)
        
        await add_leadeboard_reaction(message, reactions)

        await message.edit(embed=embed)


def wrong_channel_prompt(desc):
    return discord.Embed(
        title='Oooooops! Seems like a Wrong channel :(',
        description=desc,
    ).set_thumbnail(
        url='https://media.tenor.com/images/2b454269146fcddfdae60d3013484f0f/tenor.gif'
    )


async def check_channel_ask_a_bot(message):
    ch = message.channel
    if ch.id != int(os.environ['ASK_A_BOT']) and type(ch).__name__ != 'DMChannel':
        prompt = wrong_channel_prompt(
            "Type this command in 'Ask-a-Bot channel' or DM the bot to get the desired result !! ")
        asyncio.ensure_future(ch.send(embed=prompt))
        return False
    else:
        return True
