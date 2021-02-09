from utils import not_recognized, data_not_found
from services.user import get_user_email_and_id, submit_user_details
from services.content import fetch, mark_ques_status, get_leaderboard, check_channel_ask_a_bot
from services.mmt import assign_mentors_to_all
from services.report import get_report_from_db, show_user_report, calc_days
import discord
import os
from dotenv import load_dotenv
import requests
import asyncio
load_dotenv()

#no oops ;-;
last_leaderboard_message_id=None
current_leaderboard_page_number=1

def update_current_leaderboard_page_number(page):
    global current_leaderboard_page_number
    current_leaderboard_page_number=page

def get_prompt_help():
    return discord.Embed(
          title='DN Bot Guide', description= "DN Bot is especially designed for the users of Devsnest Community."
          + "DN bot is always there to help and make your learning fun. Use the below commands for smooth experience on the platform \n"
        ).set_thumbnail(
            url = 'https://cdn.wayscript.com/blog_img/83/DiscordBotThumb.png'
        )


async def on_user_message(message):
    if message.content.startswith('dn-assign-mentors'):
        asyncio.ensure_future(assign_mentors_to_all())

    if message.content.startswith('dn-hello'):
        msg = 'hello {0.author.mention}'.format(message)
        asyncio.ensure_future(message.channel.send(msg))

    if message.content.startswith('dn-help'):
        msg = 'dn-help: To get command help \n \n dn-fetch: To get list of questions \n \n dn-mark-done: To mark question done \n \n dn-mark-undone: To mark question undone \n \n dn-mark-doubt: To get mark question as doubt \n \n dn-report: To get progress report \n \n dn-leaderboard: To get list of top 10 students of week \n '

        prompt = get_prompt_help()
        prompt.add_field(
            name="Here is your ultimate guide to DN bot.\n",
            value=msg,
            inline=False)

        asyncio.ensure_future(message.channel.send(embed=prompt))

    if message.content.startswith('dn-email'):
        user_email = await get_user_email_and_id(message.author)
        if user_email:
            asyncio.ensure_future(submit_user_details(message.author,user_email))

    if message.content.startswith('dn-fetch'):
        if await check_channel_ask_a_bot(message):
            asyncio.ensure_future(fetch(message))

    if message.content.startswith('dn-mark-done'):
        if await check_channel_ask_a_bot(message):
            asyncio.ensure_future(mark_ques_status(message.author, message, 0))


    if message.content.startswith('dn-mark-undone'):
        if await check_channel_ask_a_bot(message):
            asyncio.ensure_future(mark_ques_status(message.author, message, 1))


    if message.content.startswith('dn-mark-doubt'):
        if await check_channel_ask_a_bot(message):
            asyncio.ensure_future(mark_ques_status(message.author, message, 2))

    if message.content.startswith('dn-report'):
        if await check_channel_ask_a_bot(message):
            days = await calc_days(message)
            if days:
                resp = await get_report_from_db(message, days)
                # ToDo report handling
                asyncio.ensure_future(show_user_report(resp, message, days))

    if message.content.startswith('dn-leaderboard'):
        if await check_channel_ask_a_bot(message):
            global current_leaderboard_page_number
            global last_leaderboard_message_id
            
            try:
                current_leaderboard_page_number = int(message.content.split(' ')[1])
            except:
                current_leaderboard_page_number = 1

            last_leaderboard_message_id=await get_leaderboard(message,current_leaderboard_page_number)

