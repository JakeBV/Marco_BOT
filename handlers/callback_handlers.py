from config import angel
from config import me
from misc import bot
from misc import dp
from services import keyboards
from services import mongo
from services.states import PrivateStates


@dp.callback_query_handler(lambda callback: callback.data == 'create_memes', chat_type='private', state='*')
async def create_memes(callback_query):
    user_id = callback_query.from_user.id
    await bot.answer_callback_query(callback_query.id)
    await dp.current_state(user=user_id, chat=user_id).set_state(PrivateStates.P1_CREATE_MEMES)
    await bot.edit_message_text('Отправь <b>картинку с подписью</b>, текст которой должен быть на меме. Подпись должна '
                                'быть в таком формате:\n<code>Верхняя строка\nНижняя строка</code>\nЕсли надпись нужна '
                                'только снизу или только сверху, используй символ <b>*</b> для указания отсутствия надп'
                                'иси, например:\n<code>Верхняя строка\n*</code>\nили\n<code>*\nНижняя строка</code>',
                                user_id, callback_query.message.message_id, reply_markup=keyboards.cancel_button())


@dp.callback_query_handler(lambda callback: callback.data == 'send', chat_type='private', state='*')
async def send_message_to_chat(callback_query):
    user_id = callback_query.from_user.id
    await bot.answer_callback_query(callback_query.id)
    await dp.current_state(user=user_id, chat=user_id).set_state(PrivateStates.P2_SEND_MESSAGE)
    await bot.edit_message_text('Пришли сообщение, которое нужно отправить', user_id, callback_query.message.message_id,
                                reply_markup=keyboards.cancel_button())


@dp.callback_query_handler(lambda callback: callback.data == 'stickers', chat_type='private', state='*')
async def stickers_list(callback_query):
    user_id = callback_query.from_user.id
    stickers = (await mongo.find('admins_panel'))['stickers']
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text('Стикерпаки', user_id, callback_query.message.message_id,
                                reply_markup=keyboards.stickers_keyboard(user_id in (me, angel), stickers))


@dp.callback_query_handler(lambda callback: callback.data == 'add_stickers', chat_type='private', state='*')
async def add_stickers(callback_query):
    user_id = callback_query.from_user.id
    await bot.answer_callback_query(callback_query.id)
    await dp.current_state(user=user_id, chat=user_id).set_state(PrivateStates.P3_ADD_STICKERS)
    await bot.edit_message_text('Пришли мне название пака и ссылку на него в таком формате:\n<code>Attack on Titan '
                                'Anime | https://t.me/addstickers/Attack_on_Titan_Anime</code>', user_id,
                                callback_query.message.message_id, reply_markup=keyboards.cancel_button())


@dp.callback_query_handler(lambda callback: callback.data == 'del_stickers', chat_type='private', state='*')
async def del_stickers(callback_query):
    user_id = callback_query.from_user.id
    stickers = (await mongo.find('admins_panel'))['stickers']
    await bot.answer_callback_query(callback_query.id)
    await dp.current_state(user=user_id, chat=user_id).set_state(PrivateStates.P4_DEL_STICKERS)
    await bot.send_message(user_id, 'Нажми на стикерпак, который нужно удалить из меню',
                           reply_markup=keyboards.del_stickers_keyboard(stickers))


@dp.callback_query_handler(lambda callback: callback.data == 'cancel', chat_type='private', state='*')
async def cancel(callback_query):
    user_id = callback_query.from_user.id
    await bot.answer_callback_query(callback_query.id)
    await dp.current_state(user=user_id, chat=user_id).finish()
    await bot.edit_message_text('Привет! Я - Марко БОТ. Выбери команду', user_id, callback_query.message.message_id,
                                reply_markup=keyboards.start_keyboard(user_id in (me, angel)))


@dp.callback_query_handler(chat_type='private', state='p4_del_stickers')
async def confirm_del_stickers(callback_query):
    user_id = callback_query.from_user.id
    await mongo.update('admins_panel', {'$unset': {f'stickers.{callback_query.data}': {}}})
    stickers = (await mongo.find('admins_panel'))['stickers']
    await bot.answer_callback_query(callback_query.id)
    await dp.current_state(user=user_id, chat=user_id).finish()
    await bot.send_message(user_id, 'Стикерпак успешно удален',
                           reply_markup=keyboards.stickers_keyboard(user_id in (me, angel), stickers))
