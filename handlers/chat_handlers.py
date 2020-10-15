from asyncio import sleep
from os import path
from random import choice

from aiogram.utils.exceptions import BadRequest

from config import snk_chat
from misc import bot
from misc import dp
from services import keyboards
from services import mongo
from utils import json_worker


@dp.message_handler(is_chat_admin=True, chat_id=snk_chat, text='!tweaks', state='*')
async def activity_settings(message):
    activity = json_worker.read_json(path.join('data', 'weights.json'))
    activity_keyboard, text = keyboards.activity_settings_keyboard(activity[0])
    await message.reply(f'Тут можно настроить мою активность. {text}', reply_markup=activity_keyboard)


@dp.message_handler(is_imitation_talk=True, chat_id=snk_chat, content_types='any', state='*')
async def imitation_talk(message):
    messages = (await mongo.find('messages'))['messages']
    text = choice(messages)
    typing_time = len(text) / 6
    await bot.send_chat_action(message.chat.id, 'typing')
    await sleep(typing_time)
    try:
        await message.reply(text, reply=choice([True, False]))
    except BadRequest:
        await message.reply(text, reply=False)


@dp.callback_query_handler(is_activity_settings=True, is_chat_admin=True, chat_id=snk_chat, state='*')
async def callback_tweaks(callback_query):
    activities, popup_text = keyboards.activities_dict[callback_query.data]
    await bot.answer_callback_query(callback_query.id, text=popup_text)
    weights = [activities, 100 - activities]
    json_worker.write_json(weights, path.join('data', 'weights.json'))
    activity_keyboard, text = keyboards.activity_settings_keyboard(activities)
    if not activities:
        text = f'{text} <a href="https://telegra.ph/file/0e4eacaff1e08e039acc7.gif">​</a>'
    await bot.edit_message_text(f'Тут можно настроить мою активность. {text}', callback_query.message.chat.id,
                                callback_query.message.message_id, reply_markup=activity_keyboard)
