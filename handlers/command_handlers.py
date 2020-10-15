from misc import bot
from misc import dp
from services import mongo
from utils import release_calendar


@dp.message_handler(commands='help', state='*')
async def help_message(message):
    await message.reply('<code>!tweaks</code>: Настройка активности (только в чате)\n<code>? your text</code>: '
                        'Перевести сообщение после вопросительного знака на русский\n<code>! your text</code>: '
                        'Перевести сообщение после восклицательного знака на украинский\n<code>?</code> или <code>!'
                        '</code> (только реплай): Перевести сообщение на русский/украинский\n<code>!lang</code> '
                        '(только реплай): Информация о языке в сообшении')


@dp.message_handler(commands='when', state='*')
async def when_message(message):
    dates = await mongo.find('admins_panel')
    await bot.send_message(message.chat.id, release_calendar.days_counter(dates))
