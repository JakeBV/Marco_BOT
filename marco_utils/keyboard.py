import random

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


verified_dict = {'intruder': 'Я вторженец',
                 'robot': 'Я робот',
                 'human': 'Я человек'}

activities_dict = {'turn_off': [0, '👍🏿'],
                   'seldom': [25, 'Буду отвечать с вероятностью 25%'],
                   'sometimes': [50, 'Буду отвечать с вероятностью 50%'],
                   'often': [75, 'Буду отвечать с вероятностью 75%']}

start_dict = {'gif': 'Отправить GIF', 'rascal': 'Отправить GIF (Енот Раскал)', 'sticker': 'Отправить стикер',
              'chimi-chara': 'Отправить стикер (Chimi-Chara)', 'chimi-chara-2': 'Отправить стикер (Chimi-Chara Part 2)',
              'when': 'Когда новая серия или глава?'}


def activity_settings_keyboard(current_activity):
    buttons = {0: ('turn_off', 'Отключить', 'Сейчас она <b>отключена</b>'),
               25: ('seldom', 'Редко', 'Сейчас я <b>редко</b> ее проявляю'),
               50: ('sometimes', 'Иногда', 'Сейчас я <b>иногда</b> ее проявляю'),
               75: ('often', 'Часто', 'Сейчас я <b>часто</b> ее проявляю')}
    activity_keyboard = InlineKeyboardMarkup()
    buttons_list = []
    text = ''
    for probability, button_and_text in buttons.items():
        if probability != current_activity:
            buttons_list.append(InlineKeyboardButton(button_and_text[1], callback_data=button_and_text[0]))
        else:
            text = button_and_text[2]
    activity_keyboard.row(*buttons_list)
    return activity_keyboard, text


def new_member_keyboard(user_id):
    member_keyboard = InlineKeyboardMarkup()
    for k, v in sorted(verified_dict.items(), key=lambda x: random.random()):
        member_keyboard.add(InlineKeyboardButton(v, callback_data=f'{k}={user_id}'))
    return member_keyboard


def spam_keyboard(user_id):
    sp_keyboard = InlineKeyboardMarkup()
    spam_dict = {'block': 'Выставить за Стены',
                 'disable_antispam': 'Отключить антиспам'}
    for k, v in spam_dict.items():
        sp_keyboard.add(InlineKeyboardButton(v, callback_data=f'{k}={user_id}'))
    return sp_keyboard


def start_keyboard(its_admin):
    st_keyboard = InlineKeyboardMarkup()
    st_keyboard.add(InlineKeyboardButton('Чат', url='t.me/shingeki_no_kyojin'))
    for k, v in start_dict.items():
        st_keyboard.add(InlineKeyboardButton(v, switch_inline_query=k))
    st_keyboard.add(InlineKeyboardButton('Стикерпак', url='https://t.me/addstickers/Attack_on_Titan_Anime'))
    st_keyboard.add(InlineKeyboardButton('Сделать и отправить мем', callback_data='create_memes'))
    if its_admin:
        st_keyboard.add(InlineKeyboardButton('Отправить сообщение в чат', callback_data='send'))
    return st_keyboard


def memes_send(file_id):
    return InlineKeyboardMarkup().add(InlineKeyboardButton('Отправить', switch_inline_query=f'send_memes={file_id}'))


def cancel_button():
    return InlineKeyboardMarkup().add(InlineKeyboardButton('Отмена', callback_data='cancel'))
