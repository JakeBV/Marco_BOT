from uuid import uuid4

from aiogram.types import InlineQueryResultCachedPhoto
from aiogram.types import InlineQueryResultArticle
from aiogram.types import InputTextMessageContent
from aiogram.utils.exceptions import BadRequest

from misc import bot
from misc import dp
from services import mongo
from utils import release_calendar


@dp.inline_handler(is_send_memes=True, state='*')
async def send_memes(inline_query):
    try:
        file_id = inline_query.query.split('=')[1]
        memes = [InlineQueryResultCachedPhoto(id=uuid4().hex, photo_file_id=file_id)]
        await bot.answer_inline_query(inline_query.id, memes, switch_pm_text='Другие команды',
                                      switch_pm_parameter='start')
    except BadRequest:
        text = 'Я делаю мемасы с помощью @marco_bot'
        article = [InlineQueryResultArticle(id=uuid4().hex, input_message_content=InputTextMessageContent(text),
                                            title='Поделиться ссылкой на меня')]
        await bot.answer_inline_query(inline_query.id, article, switch_pm_text='Другие команды',
                                      switch_pm_parameter='start')


@dp.inline_handler(lambda inline: inline.query == 'when', state='*')
async def send_when(inline_query):
    dates = await mongo.find('admins_panel')
    text = release_calendar.days_counter(dates).replace('У меня', 'Сейчас')
    article = [InlineQueryResultArticle(id=uuid4().hex, input_message_content=InputTextMessageContent(text),
                                        title=text[text.index('\n') + 1:])]
    await bot.answer_inline_query(inline_query.id, article, switch_pm_text='Другие команды',
                                  switch_pm_parameter='start')
