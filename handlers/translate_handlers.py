from config import translator
from config import snk_chat
from misc import bot
from misc import dp


@dp.message_handler(text_startswith=['! ', '? '], state='*')
async def translate_message(message):
    destination = 'ru' if message.text[0] == '?' else 'uk'
    text = translator.translate(message.text[2:], dest=destination).text
    if text:
        await message.reply(text)


@dp.message_handler(is_reply_text=True, text=['!', '?'], state='*')
async def translate_reply(message):
    to_translate = message.reply_to_message.text or message.reply_to_message.caption
    destination = 'ru' if message.text[0] == '?' else 'uk'
    text = translator.translate(to_translate, dest=destination).text
    await bot.send_message(message.chat.id, text, reply_to_message_id=message.reply_to_message.message_id)


@dp.message_handler(is_ukrainian=True, chat_id=snk_chat, state='*')
async def translate_ukrainian(message):
    text = translator.translate(message.text, dest='ru').text
    await message.reply(text)


@dp.message_handler(is_reply_text=True, text='!lang', state='*')
async def detect_language(message):
    detect = translator.detect(message.reply_to_message.text or message.reply_to_message.caption)
    text = f'Язык: {detect.lang}\nТочность: {detect.confidence:.0%}'
    await bot.send_message(message.chat.id, text, reply_to_message_id=message.reply_to_message.message_id)
