import discord
import requests

from utils import take_input_dm, not_recognized

BASE_URL = 'http://localhost:3000/api/v1/contents'


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

        value = 'Use this command to fetch : ' + \
            '`' + content[i]['unique_id'] + '`'

        if content[i]['link']:
            value = '[Link]({0})'.format(content[i]['link'])

        embed.add_field(
            name=content[i]['name'].capitalize(),
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
    
    # res = requests.get(BASE_URL+'?filter[parent_id]=' + unique_id)

    print(BASE_URL+'?filter[parent_id]=' + unique_id)
    url = BASE_URL+'?filter[parent_id]=' + unique_id
    res={}
    
    embed = discord.Embed(
        title='Resource',
        description='Choose the resource by typing out the name of the resource',
    )
    
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers,data=payload)
    data=response.json()
    
    if(not data.status_code == 200):
        return False
    else:
        content = extract_content(res)
        
        if not content:
            return False

        await prompt_and_check(user, embed, content, False)
    
    return True


async def fetch(user, command):

    command = command.content.split(' ')

    if len(command) > 1:
        return await fetch_content(user,command[1])
    
    embed = discord.Embed(
        title='Resource',
        description='Choose the resource by typing out the name of the resource',
    )

    payload = {}
    headers = {}

    #BASE_URL= 'http://127.0.0.1:3000/api/v1/contents'
    response = requests.request("GET", BASE_URL, headers=headers, data=payload)
    data=response.json()

    curriculums = extract_content(data)
    if not curriculums:
        return False

    user_input = await prompt_and_check(user, embed, curriculums)
    if not user_input:
        return False
    
    url=BASE_URL + '?filter[parent_id]=' + user_input.content
    response = requests.request("GET", url, headers=headers, data=payload)
    data=response.json()

    subtopics = extract_content(data)

    if not subtopics:
        return False

    user_input = await prompt_and_check(user, embed, subtopics)
    if not user_input:
        return False

    return True


async def mark_done(user,command):
  unique_id=command.content.split(' ')[1]
  status = 1
  res = await update_submissions(user,unique_id,status)
  
  embed = discord.Embed(
  title='Resource',
  description='Marked done',
  )
  
  if not res.status_code == 200:
      return False

  else:
      content=extract_content(res)
      
      if not content:
          return False
      
      await prompt_and_check(user,embed,content,False)


async def mark_undone(user,command):
  unique_id=command.content.split(' ')[1]
  status = 0
  res = await update_submissions(user,unique_id,status)


  embed = discord.Embed(
    title='Resource',
    description='Marked undone',
  )
  
  if not res.status_code == 200:
      return False

  else:
      content=extract_content(res)
      
      if not content:
          return False
      
      await prompt_and_check(user,embed,content,False)



async def mark_doubt(user,command):
  unique_id=command.content.split(' ')[1]
  status = 2
  res = await update_submissions(user,unique_id,status)


  embed = discord.Embed(
    title='Resource',
    description='Marked undone',
  )
  print(unique_id)
  
  res={}  #get response
  
  if not res.status_code == 200:
      return False

  else:
      content=extract_content(res)
      
      if not content:
          return False
      
      await prompt_and_check(user,embed,content,False)



async def update_submissions(user,unique_id,status):
  id = user.id
  url = 'http://127.0.0.1:3000/api/v1/submissions'
  headers = {
      'Content-Type': 'application/vnd.api+json'
  }

  myobj = {
    "data":{
      "attributes":{
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