from misc import bot
from misc import dp
from services import mongo
from utils import release_calendar


@dp.message_handler(commands='when', state='*')
async def when(message):
    dates = await mongo.find('admins_panel')
    await bot.send_message(message.chat.id, release_calendar.days_counter(dates))
