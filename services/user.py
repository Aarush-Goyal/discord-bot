import discord
import re
import asyncio
import requests

from client import client


async def get_user_email_and_id(user):
    prompt = discord.Embed(
        title='Welcome new User', description='Please enter your Email ID')

    await user.send(embed=prompt)

    async def validate_email(email):
        email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        return re.search(email_regex, email.content)

    def check(message):
      return message.channel==user.dm_channel

    try:
        email = await client.wait_for("message", check=check ,timeout=60)
        if await validate_email(email):
            await user.send('your recieved email : {0}'.format(
                email.content))
        else:
            await user.send(
                'Email not valid , pls try again with `-email` command')
            email=False

    except asyncio.TimeoutError:
        await user.send(
            'Sorry, You didn\'t replied in time, Please send `-email` again to get the prompt again.'
        )
        email = False

    return email


async def submit_details(user_email,user):
    # TODO Error Handling on status!=200
    url = 'https://jsonplaceholder.typicode.com/signup'
    myobj = {
        "data": {
          "attributes":{
            "email": user_email.content,
            "name": "discord"+user.name,
            "discord_id": str(user.id),
            "username":user.name,
            "password": "Prachi@1777",
            "buddy":0
          },
          "type":"users"
        }
    }
    print(myobj)
    x = requests.post(url, json=myobj)
    print(x)