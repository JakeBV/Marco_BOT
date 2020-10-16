from config import snk_chat
from misc import dp
from services import mongo
from utils import release_calendar


@dp.message_handler(commands='help', state='*')
async def help_message(message):
    text = ''
    if message.chat.id == snk_chat:
        text = '<code>!tweaks</code>:  Настройка моей активности (только администраторы чата)\n'
    await message.reply(text + '<code>? your text</code>:  Перевести текст после вопросительного знака на русский\n'
                               '<code>! your text</code>:  Перевести текст после восклицательного знака на украинский\n'
                               '<code>?</code> или <code>!</code> (только реплай):  Перевести сообщение на русский/'
                               'украинский\n<code>!lang</code> (только реплай):  Определить язык сообщения\n<code>'
                               '!about</code>:  Исходники', reply=text)


@dp.message_handler(commands='when', state='*')
async def when_message(message):
    dates = await mongo.find('admins_panel')
    await message.reply(release_calendar.days_counter(dates), reply=message.chat.id == snk_chat)


@dp.message_handler(text='!about', state='*')
async def about_message(message):
    await message.reply('<a href="https://github.com/JakeBV/marco_bot">Исходники бота</a>',
                        reply=message.chat.id == snk_chat)
