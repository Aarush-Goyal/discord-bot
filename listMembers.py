from client import client
from logger import infoLogger
from services.user import submit_user_details
async def listExistingMembers():
    for member in client.get_all_members():
        if not member.bot:
            infoLogger.info('database call to create '+str(member.name)+' with id '+ str(member.id)+' is sent.')
            await submit_user_details(member)

