from asyncio import sleep
from datetime import timedelta
from re import search
from time import time

from aiogram.utils.exceptions import MessageToEditNotFound
from aiogram.utils.exceptions import MessageToDeleteNotFound
from aiogram.utils.exceptions import MessageNotModified

from config import angel
from config import me
from config import snk_chat
from misc import bot
from misc import dp
from services import spam_checks
from services import keyboards
from services import mongo
from services.states import VerificationStates
from utils import utils


@dp.message_handler(is_angel=True, chat_id=snk_chat, content_types='new_chat_members', state='*')
async def return_rights(message):
    await bot.delete_message(snk_chat, message.message_id)
    await bot.promote_chat_member(snk_chat, angel, can_delete_messages=True, can_invite_users=True,
                                  can_restrict_members=True, can_pin_messages=True, can_promote_members=True,
                                  can_change_info=True)
    await bot.set_chat_administrator_custom_title(snk_chat, angel, 'Анхель')
    await bot.send_message(snk_chat, f'С возвращением, <a href="tg://user?id={angel}">'
                                     f'{message.from_user.first_name}</a>!\nДержи свой значок и пистолет')


@dp.message_handler(lambda message: message.from_user.id != me, chat_id=snk_chat, content_types='new_chat_members',
                    state='*')
async def new_chat_members(message):
    await bot.delete_message(snk_chat, message.message_id)
    for user in message.new_chat_members:
        first_name = user.first_name
        user_id = user.id
        if bool(search(u"[\u0621-\u064a]+", first_name)):
            await bot.send_message(snk_chat, f'<a href="tg://user?id={user_id}">{first_name}</a> '
                                             f'выставлен(а) за Стены. Мне не нравится это имя')
            await bot.kick_chat_member(snk_chat, user_id, until_date=int(time() + 60))

        elif not user.is_bot:
            message_id = (await bot.send_message(snk_chat, f'Приветствую в чате SnK, <a href="tg://user?id={user_id}">'
                                                           f'{first_name}</a>! Пожалуйста, докажи, что ты не робот или'
                                                           f' вторженец, нажав кнопку ниже. На это у тебя есть минута',
                                                 reply_markup=keyboards.new_member_keyboard(user_id))).message_id
            await dp.current_state(user=user_id, chat=snk_chat).set_state(VerificationStates.S1_NOT_VERIFICATION)
            await sleep(65)
            if await dp.current_state(user=user_id, chat=snk_chat).get_state() == 's1_not_verification':
                try:
                    await bot.edit_message_text(f'<a href="tg://user?id={user_id}">{first_name}</a> '
                                                f'выставлен(а) за Стены. Проверка не пройдена',
                                                snk_chat, message_id)
                except MessageToEditNotFound:
                    await bot.send_message(snk_chat, f'<a href="tg://user?id={user_id}">{first_name}</a> '
                                                     f'выставлен(а) за Стены. Проверка не пройдена')
                await bot.kick_chat_member(snk_chat, user_id)
                await bot.unban_chat_member(snk_chat, user_id)


@dp.message_handler(chat_id=snk_chat, content_types='left_chat_member', state='*')
@dp.message_handler(chat_id=snk_chat, content_types='any', state='s1_not_verification')
async def del_message(message):
    await bot.delete_message(snk_chat, message.message_id)


@dp.edited_message_handler(is_new_user=True, is_spam=True, chat_id=snk_chat, content_types='any',
                           state='s2_verification')
@dp.message_handler(is_new_user=True, is_spam=True, chat_id=snk_chat, content_types='any', state='s2_verification')
async def hunt_for_spam(message):
    user_id = message.from_user.id
    message_id = message.message_id
    get_users_info = (await mongo.find('new_chat_members'))['new_chat_members'][f'{user_id}']
    join_time = get_users_info['join_time']
    if message.entities or message.caption_entities:
        entities = message.entities or message.caption_entities
        text = message.text or message.caption
        its_spam = await spam_checks.search_entities(entities, text)
        clarification = 'Сообщение'
    else:
        its_spam = spam_checks.search_urls_in_keyboard(message.reply_markup.inline_keyboard)
        text = '\n'.join(its_spam)
        clarification = 'Ссылки в клавиатуре'
    if its_spam:
        await bot.delete_message(snk_chat, message_id)
        image_url = utils.upload_photo(utils.text_to_image(text, message_id))
        member_time = time() - join_time
        remaining_time = str(timedelta(seconds=86400 - member_time)).split('.')[0]
        await bot.send_message(snk_chat, f'<a href="tg://user?id={user_id}">{get_users_info["first_name"]}</a>, тебе '
                                         f'запрещено отправлять ссылки еще {remaining_time}!\n\n{clarification}:'
                                         f'<a href="https://telegra.ph/{image_url}">​</a>',
                               reply_markup=keyboards.spam_keyboard(user_id))


@dp.callback_query_handler(is_verification=True, chat_id=snk_chat, state='*')
async def callback_verified(callback_query):
    who_is_it, unknown_id = callback_query.data.split('=')
    user_id = callback_query.from_user.id
    first_name = callback_query.from_user.first_name
    message_id = callback_query.message.message_id
    if int(unknown_id) == user_id:
        await bot.answer_callback_query(callback_query.id)
        if who_is_it in ('robot', 'intruder'):
            try:
                it_is = keyboards.verified_dict[who_is_it].split()[-1].title()
                await bot.edit_message_text(f'<a href="tg://user?id={user_id}">{it_is}</a>? Подумай еще', snk_chat,
                                            message_id, reply_markup=keyboards.new_member_keyboard(user_id))
            except MessageNotModified:
                await bot.edit_message_text('Это уже начинает надоедать', snk_chat, message_id,
                                            reply_markup=keyboards.new_member_keyboard(user_id))
        else:
            await dp.current_state(user=user_id, chat=snk_chat).set_state(VerificationStates.S2_VERIFICATION)
            users_info = {'first_name': first_name,
                          'username': callback_query.from_user.username,
                          'join_time': int(time()),
                          'message_id': message_id}
            await mongo.update('new_chat_members', {'$set': {f'new_chat_members.{user_id}': users_info}})
            await bot.edit_message_text(f'Отлично, <a href="tg://user?id={user_id}">{first_name}</a> проверка пройдена!'
                                        ' Приятного времяпрепровождения в чате, однако тебе запрещено отправлять ссылки'
                                        ' еще 24 часа', snk_chat, message_id)
    else:
        await bot.answer_callback_query(callback_query.id, show_alert=True, text='Ты не тыкай, это не тебе!')


@dp.callback_query_handler(is_antispam_settings=True, chat_id=snk_chat, state='*')
async def antispam_settings(callback_query):
    message_id = callback_query.message.message_id
    is_admin = callback_query.from_user.id in [admin.user.id for admin in await bot.get_chat_administrators(snk_chat)]
    if is_admin:
        await bot.answer_callback_query(callback_query.id)
        call_data, user_id = callback_query.data.split('=')
        first_name = (await mongo.find('new_chat_members'))['new_chat_members'][user_id]['first_name']
        if call_data == 'disable_antispam':
            await dp.current_state(user=int(user_id), chat=snk_chat).finish()
            await bot.edit_message_text(f'Антиспам у <a href="tg://user?id={user_id}">{first_name}</a> отключен.\nЭто '
                                        f'сообщение удалится через 15 секунд', snk_chat, message_id)
        else:
            await bot.edit_message_text(f'<a href="tg://user?id={user_id}">{first_name}</a> выставлен(а) за Стены.\nЭто'
                                        f' сообщение удалится через 15 секунд', snk_chat, message_id)
            await bot.kick_chat_member(snk_chat, int(user_id), until_date=int(time()) + 600)
        await sleep(20)
        try:
            await bot.delete_message(snk_chat, message_id)
        except MessageToDeleteNotFound:
            pass
    else:
        await bot.answer_callback_query(callback_query.id, show_alert=True, text='Ты мне не тыкай!')
