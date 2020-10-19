from io import BytesIO

from aiogram.types import InputMediaPhoto

from config import angel
from config import me
from config import snk_chat
from misc import bot
from misc import dp
from services import keyboards
from services import mongo
from utils import meme_creator
from utils import utils


@dp.message_handler(chat_type='private', state='p1_create_memes', content_types=['text', 'photo'])
async def create_memes(message):
    user_id = message.from_user.id
    if (message.caption is None) or (len(message.caption.splitlines()) != 2):
        await message.reply('Отправь <b>картинку с подписью</b>. Подпись должна быть в таком формате:\n<code>Верхняя '
                            'строка\nНижняя строка</code>\nили\n<code>Верхняя строка\n*</code>\nили\n<code>*\nНижняя '
                            'строка</code>', reply=False, reply_markup=keyboards.cancel_button())
    else:
        top_string, bottom_string = message.caption.splitlines()
        if len(top_string) > 89 or len(bottom_string) > 89:
            await message.reply('Каждая строка должна быть не более 90 символов, включая пробелы', reply=False,
                                reply_markup=keyboards.cancel_button())
        else:
            hourglass = 'https://telegra.ph/file/cc0dc4ff9bf6be68d5f63.gif'
            message_id = (await bot.send_animation(user_id, hourglass)).message_id
            await bot.send_chat_action(message.chat.id, 'upload_photo')
            downloaded = await bot.download_file_by_id(message.photo[-1].file_id)
            image = BytesIO()
            image.write(downloaded.getvalue())
            ready_top_string, ready_bottom_string = meme_creator.prepare_text(top_string, bottom_string)
            memes = meme_creator.make_meme(ready_top_string, ready_bottom_string, image, user_id)
            file_id = (await bot.edit_message_media(InputMediaPhoto(memes), user_id, message_id)).photo[-1].file_id
            await bot.edit_message_caption(user_id, message_id, caption='Готово!',
                                           reply_markup=keyboards.memes_send(file_id))


@dp.message_handler(chat_type='private', state='p2_send_message', content_types=['text', 'photo', 'sticker'])
async def send_message_to_chat(message):
    user_id = message.from_user.id
    if message.text:
        await bot.send_message(snk_chat, message.text)
    elif message.sticker:
        await bot.send_sticker(snk_chat, message.sticker.file_id)
    else:
        await bot.send_photo(snk_chat, message.photo[-1].file_id, message.caption)
    await dp.current_state(user=user_id, chat=user_id).finish()
    await message.reply('Сообщение отправлено', reply_markup=keyboards.start_keyboard(user_id in (me, angel)),
                        reply=False)


@dp.message_handler(chat_type='private', state='p3_add_stickers', content_types='text')
async def add_stickers(message):
    user_id = message.from_user.id
    stickers = (await mongo.find('admins_panel'))['stickers']
    if utils.check_validity_stickerpack(message.text, stickers):
        stickers_title, stickers_link = message.text.split('|')
        await mongo.update('admins_panel', {'$set': {f'stickers.{stickers_title.strip()}': stickers_link.strip()}})
        stickers = (await mongo.find('admins_panel'))['stickers']
        await dp.current_state(user=user_id, chat=user_id).finish()
        await message.reply('Стикерпак успешно добавлен', reply=False,
                            reply_markup=keyboards.stickers_keyboard(user_id in (me, angel), stickers))
    else:
        await message.reply('Неверный формат или стикерпак уже добавлен', reply=False,
                            reply_markup=keyboards.cancel_button())


@dp.message_handler(chat_type='private', state='*')
async def start(message):
    user_id = message.from_user.id
    users_in_db = (await mongo.find('new_chat_members'))['users']
    if str(user_id) not in users_in_db and user_id != me:
        users_info = {'first_name': message.from_user.first_name,
                      'username': message.from_user.username}
        await mongo.update('new_chat_members', {'$set': {f'users.{user_id}': users_info}})
    await message.reply('Привет! Я - Марко БОТ. Выбери команду', reply=False,
                        reply_markup=keyboards.start_keyboard(user_id in (me, angel)))
