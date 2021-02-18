import requests

from client import client
from logger import errorLogger, infoLogger
from services.user import submit_user_details
from utils import send_request


async def listExistingMembers():
    res = await getAllMembers()
    d = {}
    for i in res["data"]:
        d[int(i["attributes"]["discord_id"])] = 1
    for member in client.get_all_members():
        if not member.bot:
            if member.id not in d:
                infoLogger.info(
                    "database call to create "
                    + str(member.name)
                    + " with id "
                    + str(member.id)
                    + " is sent."
                )
                await submit_user_details(member)


async def getAllMembers():
    url = "api/v1/users"
    try:
        res = await send_request("GET", url)
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
        errorLogger("error in fetching users from db" + str(e))
    res = res.json()
    return res
