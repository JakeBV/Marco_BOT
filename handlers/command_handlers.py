from os import path

from config import snk_chat
from misc import bot
from misc import dp
from services import keyboards
from services import mongo
from utils import json_worker
from utils import release_calendar


@dp.message_handler(is_chat_admin=True, chat_id=snk_chat, commands='tweaks', state='*')
async def activity_settings(message):
    activity = json_worker.read_json(path.join('data', 'weights.json'))
    activity_keyboard, text = keyboards.activity_settings_keyboard(activity[0])
    await message.reply(f'Тут можно настроить мою активность. {text}', reply_markup=activity_keyboard, reply=True)


@dp.message_handler(commands='when', state='*')
async def when(message):
    dates = await mongo.find('admins_panel')
    await bot.send_message(message.chat.id, release_calendar.days_counter(dates))
