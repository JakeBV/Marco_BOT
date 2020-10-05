import random
import re
import asyncio
import time
import configparser
import json
from uuid import uuid4
from datetime import timedelta
from io import BytesIO

from aiogram import Bot, types
from aiogram.types import ContentType
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils import exceptions
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from googletrans import Translator

from marco_utils import mongo
from marco_utils import keyboard
from marco_utils import entities_checker
from marco_utils import verification
from marco_utils import text_to_image
from marco_utils import photo_upload
from marco_utils import meme_creator
from marco_utils import release_calendar


config = configparser.ConfigParser()
config.read('config.ini')

bot = Bot(token=config['BOT']['token'], parse_mode=types.ParseMode.HTML)

translator = Translator()

dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

snk_chat = int(config['BOT']['chat'])
angel = int(config['BOT']['angel'])
me = int(config['BOT']['me'])
dump = int(config['BOT']['dump'])


@dp.message_handler(chat_id=snk_chat, commands=['tweaks'])
async def activity_settings(message):
    chat_id = message.chat.id
    admins = [admin.user.id for admin in await bot.get_chat_administrators(chat_id)]
    await bot.delete_message(chat_id, message.message_id)
    user_id = message.from_user.id
    if user_id in admins:
        activity = (await mongo.find('admins_panel'))['weights']
        get_keyboard_and_text = keyboard.activity_settings_keyboard(activity[0])
        activity_keyboard = get_keyboard_and_text[0]
        text = get_keyboard_and_text[1]
        await message.reply(f'Тут можно настроить мою активность. {text}',
                            reply_markup=activity_keyboard, reply=False)
    else:
        await bot.send_document(chat_id, 'CgADAgADZQMAAjVnEEsa-Qh9nMVnngI',
                                caption=f'<a href="tg://user?id={user_id}">Не лезь</a>, оно тебя сожрет')


@dp.message_handler(chat_id=snk_chat, content_types=[ContentType.NEW_CHAT_MEMBERS, ContentType.LEFT_CHAT_MEMBER],
                    state='*')
async def new_chat_members(message):
    chat_id = message.chat.id
    await bot.delete_message(chat_id, message.message_id)
    user_id = message.from_user.id

    if message.new_chat_members and user_id != me:
        if user_id == angel and angel in [x.id for x in message.new_chat_members]:
            await bot.promote_chat_member(snk_chat, user_id, can_delete_messages=True, can_invite_users=True,
                                          can_restrict_members=True, can_pin_messages=True, can_promote_members=True,
                                          can_change_info=True)
            await bot.send_message(chat_id,
                                   f'С возвращением, <a href="tg://user?id={user_id}">'
                                   f'{message.from_user.first_name}</a>!\nДержи свой значок и пистолет')
        else:
            for user in message.new_chat_members:
                user_first_name = user.first_name
                user_id = user.id
                if bool(re.search(u"[\u0621-\u064a]+", user_first_name)):
                    await bot.send_message(chat_id, f'<a href="tg://user?id={user_id}">{user_first_name}</a> '
                                                    f'выставлен(а) за Стены. Мне не нравится это имя')
                    await bot.kick_chat_member(chat_id, user_id, until_date=int(time.time() + 60))

                elif not user.is_bot:
                    message_id = (await bot.send_message(chat_id, f'Приветствую в чате SnK, <a href="tg:'
                                                                  f'//user?id={user_id}">{user_first_name}</a>! '
                                                                  f'Пожалуйста, докажи, что ты не робот или вторженец,'
                                                                  f' нажав кнопку ниже. У тебя на это есть минута',
                                                                  reply_markup=keyboard.new_member_keyboard(user_id))
                                  ).message_id

                    await dp.current_state(user=user_id).set_state(verification.VerificationStates.all()[0])

                    await asyncio.sleep(65)
                    state = await dp.current_state(user=user_id).get_state()
                    if state == 's1_not_verification':
                        try:
                            await bot.edit_message_text(f'<a href="tg://user?id={user_id}">{user_first_name}</a> '
                                                        f'выставлен(а) за Стены. Проверка не пройдена',
                                                        chat_id, message_id)
                        except exceptions.MessageToEditNotFound:
                            await bot.send_message(chat_id, f'<a href="tg://user?id={user_id}">{user_first_name}</a> '
                                                            f'выставлен(а) за Стены. Проверка не пройдена')
                        await bot.kick_chat_member(chat_id, user_id)
                        await bot.unban_chat_member(chat_id, user_id)


@dp.message_handler(content_types=ContentType.ANY, chat_id=snk_chat,
                    state=verification.VerificationStates.S1_NOT_VERIFICATION |
                    verification.VerificationStates.S2_VERIFICATION |
                    verification.VerificationStates.S6_START |
                    verification.VerificationStates.S5_SEND_MESSAGE |
                    verification.VerificationStates.S4_CREATE_MEMES)
async def hunt_for_spam(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    message_id = message.message_id
    state = await dp.current_state(user=user_id).get_state()

    if state == 's1_not_verification':
        await bot.delete_message(chat_id, message_id)

    elif message.entities or message.caption_entities or message.reply_markup:
        get_users_info = (await mongo.find('new_chat_members'))['new_chat_members'].get(f'{user_id}')
        if get_users_info is not None and time.time() - get_users_info['join_time'] < 86400:
            if message.reply_markup:
                its_spam = await entities_checker.search_urls_in_keyboard(message.reply_markup.inline_keyboard)
                text = '\n'.join(its_spam)
                clarification = 'Ссылки в клавиатуре'
            else:
                entities = message.entities or message.caption_entities
                text = message.text or message.caption
                its_spam = await entities_checker.search_entities(bot, entities, text)
                clarification = 'Сообщение'
            if its_spam:
                await bot.delete_message(chat_id, message_id)
                photo = photo_upload.upload_photo(text_to_image.create_image(text, user_id))
                member_time = time.time() - get_users_info['join_time']
                remaining_time = str(timedelta(seconds=86400 - member_time)).split('.')[0].split(':')
                h = f' {remaining_time[0]} ч' if remaining_time[0] != '0' else ''
                m = f' {remaining_time[1]} мин' if remaining_time[1] != '00' else ''
                if not h and not m:
                    m = ' минуту'
                await bot.send_message(chat_id,
                                       f'<a href="tg://user?id={user_id}">{get_users_info["first_name"]}</a>, тебе '
                                       f'запрещено отправлять ссылки еще{h}{m}!\n\n{clarification}:'
                                       f'<a href="https://telegra.ph/{photo}">​</a>',
                                       reply_markup=keyboard.spam_keyboard(user_id))

        else:
            await dp.current_state(user=user_id).set_state(verification.VerificationStates.all()[2])


@dp.message_handler(commands=['when'], state='*')
async def when(message):
    dates = await mongo.find('admins_panel')
    await bot.send_message(message.chat.id, release_calendar.days_counter(dates))


@dp.message_handler(chat_id=snk_chat, state='*')
async def talking(message):
    weights = (await mongo.find('admins_panel'))['weights']
    answer = random.choices([True, False], weights=weights)[0]

    if (message.text in ('!', '?') and message.reply_to_message) or message.text[:2] in ('! ', '? '):
        text = message.text[2:]
        message_id = message.message_id
        destination = 'ru' if message.text[0] == '?' else 'uk'
        if message.reply_to_message:
            text = message.reply_to_message.text
            message_id = message.reply_to_message.message_id
        text = translator.translate(text, dest=destination).text
        await bot.send_message(snk_chat, text, reply_to_message_id=message_id)

    elif translator.detect(message.text).lang == 'uk':
        text = translator.translate(message.text, dest='ru').text
        await message.reply(text, reply=True)

    elif answer:
        messages = (await mongo.find('messages'))['messages']
        text = random.choice(messages).replace('<', '&lt;')
        typing_time = len(text) / 6
        await bot.send_chat_action(message.chat.id, types.ChatActions.TYPING)
        await asyncio.sleep(typing_time)
        try:
            await message.reply(text, reply=random.choice([True, False]))
        except exceptions.BadRequest:
            await message.reply(text, reply=False)
    if 3 <= len(message.text) <= 65 and bool(re.search('[а-яА-Я]', message.text)):
        await mongo.update('messages', {'$push': {'messages': message.text}})


@dp.callback_query_handler(lambda call: call.data.split('=')[0] in keyboard.verified_dict, chat_id=snk_chat, state='*')
async def callback_verified(callback_query: types.CallbackQuery):
    who_is_it = callback_query.data.split('=')[0]
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    first_name = callback_query.from_user.first_name
    message_id = callback_query.message.message_id
    if int(callback_query.data.split('=')[1]) == user_id:
        if who_is_it in ('robot', 'intruder'):
            try:
                await bot.edit_message_text(f'{keyboard.verified_dict[who_is_it].split()[-1].title()}? '
                                            f'Подумай еще', chat_id, message_id,
                                            reply_markup=keyboard.new_member_keyboard(user_id))
            except exceptions.MessageNotModified:
                await bot.edit_message_text(f'Это уже начинает надоедать', chat_id, message_id,
                                            reply_markup=keyboard.new_member_keyboard(user_id))
        else:
            await dp.current_state(user=user_id).set_state(verification.VerificationStates.all()[1])

            users_info = {'first_name': first_name,
                          'username': callback_query.from_user.username,
                          'join_time': int(time.time()),
                          'message_id': message_id}
            await mongo.update('new_chat_members', {'$set': {f'new_chat_members.{user_id}': users_info}})

            await bot.edit_message_text(f'Отлично, <a href="tg://user?id={user_id}">{first_name}</a>,'
                                        f' проверка пройдена! Приятного времяпрепровождения в чате, однако '
                                        'тебе запрещено отправлять ссылки еще 24 часа',
                                        chat_id, message_id)
    else:
        await bot.answer_callback_query(callback_query.id, text='Ты не тыкай, это не тебе!')


@dp.callback_query_handler(lambda call: call.data in keyboard.activities_dict, chat_id=snk_chat, state='*')
async def callback_tweaks(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    admins = [admin.user.id for admin in await bot.get_chat_administrators(chat_id)]
    if callback_query.from_user.id in admins:
        get_activities_and_popup_text = keyboard.activities_dict[callback_query.data]
        activities = get_activities_and_popup_text[0]
        popup_text = get_activities_and_popup_text[1]
        await bot.answer_callback_query(callback_query.id, text=popup_text)
        weights = [activities, 100 - activities]
        await mongo.update('admins_panel', {'$set': {'weights': weights}})
        get_keyboard_and_text = keyboard.activity_settings_keyboard(activities)
        activity_keyboard = get_keyboard_and_text[0]
        text = get_keyboard_and_text[1]
        if not activities:
            text = f'{text} <a href="https://telegra.ph/file/0ab05efa3a61aeff98a46.gif">​</a>'
        await bot.edit_message_text(f'Тут можно настроить мою активность. {text}', chat_id,
                                    callback_query.message.message_id, reply_markup=activity_keyboard)
    else:
        await bot.answer_callback_query(callback_query.id, text='Ты мне не тыкай!')


@dp.callback_query_handler(lambda call: call.data, chat_id=snk_chat, state='*')
async def callback_spam(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    admins = [admin.user.id for admin in await bot.get_chat_administrators(chat_id)]
    if callback_query.from_user.id in admins:
        get_call = callback_query.data.split('=')
        call_data = get_call[0]
        user_id = int(get_call[1])
        get_users_info = (await mongo.find('new_chat_members'))['new_chat_members'][f'{user_id}']
        if call_data == 'disable_antispam':
            await dp.current_state(user=user_id).set_state(verification.VerificationStates.all()[2])
            await bot.edit_message_text(f'Антиспам у <a href="tg://user?id={user_id}">{get_users_info["first_name"]}'
                                        f'</a> отключен.\nЭто сообщение удалится через 15 секунд',
                                        chat_id, message_id)

        elif call_data == 'block':
            await bot.edit_message_text(f'<a href="tg://user?id={user_id}">{get_users_info["first_name"]}</a> '
                                        f'выставлен(а) за Стены.\nЭто сообщение удалится через 15 секунд',
                                        chat_id, message_id)
            await bot.kick_chat_member(snk_chat, user_id, until_date=int(time.time()) + 600)

        await asyncio.sleep(15)
        try:
            await bot.delete_message(chat_id, message_id)
        except exceptions.MessageToDeleteNotFound:
            pass

    else:
        await bot.answer_callback_query(callback_query.id, text='Ты мне не тыкай!')


@dp.message_handler(types.ChatType.is_private, state=verification.VerificationStates.S5_SEND_MESSAGE)
async def send_message(message: types.Message):
    user_id = message.from_user.id
    await bot.send_message(snk_chat, message.text)
    await dp.current_state(user=user_id).set_state(verification.VerificationStates.all()[5])
    await bot.send_message(user_id, 'Сообщение отправлено')


@dp.message_handler(types.ChatType.is_private, state=verification.VerificationStates.S4_CREATE_MEMES,
                    content_types=ContentType.PHOTO)
async def send_message(message: types.Message):
    user_id = message.from_user.id
    if message.caption is None:
        await bot.send_message(user_id, 'Отправь картинку с подписью', reply_markup=keyboard.cancel_button())
    else:
        strings = message.caption.splitlines()
        if len(strings) != 2:
            await bot.send_message(user_id,
                                   'Подпись должна быть в таком формате: \n<code>Это верхняя строка\n'
                                   'Это нижняя строка</code>\nили\n<code>Это верхняя строка\n*</code>\nили\n'
                                   '<code>*\nЭто нижняя строка</code>',
                                   reply_markup=keyboard.cancel_button())
        else:
            top_string, bottom_string = strings
            if len(top_string) > 89 or len(bottom_string) > 89:
                await bot.send_message(user_id, 'Каждая строка должна быть не более 90 символов, включая пробелы',
                                       reply_markup=keyboard.cancel_button())
            else:
                loading_message = (await bot.send_message(user_id, 'Минуту')).message_id
                downloaded = await bot.download_file_by_id(message.photo[-1].file_id)
                b = BytesIO()
                b.write(downloaded.getvalue())
                ready_top_string, ready_bottom_string = meme_creator.prepare_text(top_string, bottom_string)
                b = meme_creator.make_meme(ready_top_string, ready_bottom_string, b, f'{user_id}.png')
                file_id = (await bot.send_photo(dump, b)).photo[-1].file_id
                await bot.delete_message(user_id, loading_message)
                await dp.current_state(user=user_id).set_state(verification.VerificationStates.all()[5])
                await bot.send_photo(user_id, file_id, reply_markup=keyboard.memes_send(file_id))


@dp.message_handler(types.ChatType.is_private, state='*')
async def start(message: types.Message):
    user_id = message.from_user.id
    await dp.current_state(user=user_id).set_state(verification.VerificationStates.all()[5])
    users_in_db = (await mongo.find('new_chat_members'))['users']
    if str(user_id) not in users_in_db and user_id != me:
        users_info = {'first_name': message.from_user.first_name,
                      'username': message.from_user.username}
        await mongo.update('new_chat_members', {'$set': {f'users.{user_id}': users_info}})
    await bot.send_message(user_id, 'Привет! Я - Марко БОТ. Выбери команду',
                           reply_markup=keyboard.start_keyboard(True if user_id == me else False))


@dp.callback_query_handler(lambda call: call.data, state='*')
async def callback_private(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    if callback_query.data == 'create_memes':
        await dp.current_state(user=user_id).set_state(verification.VerificationStates.all()[3])
        await bot.edit_message_text(f'Отправь картинку с подписью, текст которой должен быть на меме. Подпись должна '
                                    f'быть в таком формате\n<code>Это верхняя строка\nЭто нижняя строка</code>\nЕсли '
                                    f'надпись нужна только снизу или только сверху, используй символ <code>*</code> '
                                    f'для указания отсутствия надписи, например\n<code>Это верхняя строка\n*</code>\n'
                                    f'или\n<code>*\nЭто нижняя строка</code>',
                                    chat_id, message_id,
                                    reply_markup=keyboard.cancel_button())
    elif callback_query.data == 'send':
        await dp.current_state(user=user_id).set_state(verification.VerificationStates.all()[4])
        await bot.edit_message_text(f'Пришли текст сообщения, которое нужно отправить', chat_id, message_id,
                                    reply_markup=keyboard.cancel_button())
    elif callback_query.data == 'cancel':
        await dp.current_state(user=user_id).set_state(verification.VerificationStates.all()[5])
        await bot.edit_message_text('Привет! Я - Марко БОТ. Выбери команду',
                                    chat_id, message_id,
                                    reply_markup=keyboard.start_keyboard(True if user_id == me else False))


@dp.inline_handler(lambda query: query.query, state='*')
async def inline(inline_query: types.InlineQuery):
    if inline_query.query in keyboard.start_dict and inline_query.query != 'when':
        with open('file_ids.json') as json_file:
            data = json.load(json_file)
        results = []
        for file in data[inline_query.query]:
            id_ = uuid4().hex
            if inline_query.query in ('gif', 'rascal'):
                thumb = types.InlineQueryResultCachedMpeg4Gif(id=id_, mpeg4_file_id=file)
            else:
                thumb = types.InlineQueryResultCachedSticker(id=id_, sticker_file_id=file)
            results.append(thumb)
        await bot.answer_inline_query(inline_query.id, results,
                                      switch_pm_text='Другие команды', switch_pm_parameter='start')
    elif inline_query.query.split('=')[0] == 'send_memes':
        try:
            file_id = inline_query.query.split('=')[1]
            await bot.answer_inline_query(inline_query.id,
                                          [types.InlineQueryResultCachedPhoto(id=uuid4().hex, photo_file_id=file_id)],
                                          switch_pm_text='Другие команды', switch_pm_parameter='start')
        except(exceptions.BadRequest, IndexError):
            text = 'Я делаю мемасы с помощью @marco_bot'
            await bot.answer_inline_query(
                inline_query.id,
                [types.InlineQueryResultArticle(id=uuid4().hex,
                                                input_message_content=types.InputTextMessageContent(text),
                                                title='Поделиться ссылкой на меня')],
                switch_pm_text='Другие команды', switch_pm_parameter='start')
    elif inline_query.query == 'when':
        dates = await mongo.find('admins_panel')
        text = release_calendar.days_counter(dates).replace('У меня', 'Сейчас')
        title = text.splitlines()[1]
        await bot.answer_inline_query(
            inline_query.id,
            [types.InlineQueryResultArticle(id=uuid4().hex,
                                            input_message_content=types.InputTextMessageContent(text), title=title)],
            switch_pm_text='Другие команды', switch_pm_parameter='start')


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=shutdown)
