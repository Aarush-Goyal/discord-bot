from client import client
from services.user import submit_user_details
async def listExixtingMembers():
    for member in client.get_all_members():
        print(member.name, member.id)
        await submit_user_details(member)

