from utils import not_recognized
from services.user import get_user_email_and_id, submit_user_details
from services.content import fetch, mark_ques_status
from services.mmt import assign_mentors_to_all

async def on_user_message(message):
  if message.content.startswith('-assign-mentors'):
    await assign_mentors_to_all(message)


  if message.content.startswith('-email'):
    user_email = await get_user_email_and_id(message.author)
    if user_email:
        await submit_user_details(user_email, message.author)
        print('sending')

  if message.content.startswith('-fetch'):
    response=await fetch(message.author,message)
    if not response:
      await not_recognized(message.author, '-fetch')
    
    
  if message.content.startswith('-done'):
    response=await mark_ques_status(message.author,message, 1)
    if not response:
      await not_recognized(message.author, '-fetch')

    
  if message.content.startswith('-undone'):
    response=await mark_ques_status(message.author,message, 0)
    if not response:
      await not_recognized(message.author, '-fetch')

  if message.content.startswith('-doubt'):
    response=await mark_ques_status(message.author,message, 2)
    if not response:
        await not_recognized(message.author, '-fetch')