from os import path
from random import random

from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton

from services import mongo
from utils import json_worker


verified_dict = {'intruder': 'Я вторженец',
                 'robot': 'Я робот',
                 'human': 'Я человек'}


activities_dict = {'turn_off': [0, '👍🏿'],
                   'seldom': [25, 'Буду отвечать с вероятностью 25%'],
                   'sometimes': [50, 'Буду отвечать с вероятностью 50%'],
                   'often': [75, 'Буду отвечать с вероятностью 75%']}


def activity_settings_keyboard(current_activity):
    buttons = {0: ('turn_off', 'Отключить', 'Сейчас она <b>отключена</b>'),
               25: ('seldom', 'Редко', 'Сейчас я <b>редко</b> ее проявляю'),
               50: ('sometimes', 'Иногда', 'Сейчас я <b>иногда</b> ее проявляю'),
               75: ('often', 'Часто', 'Сейчас я <b>часто</b> ее проявляю')}
    activity_keyboard = InlineKeyboardMarkup()
    text = ''
    for probability, button_and_text in buttons.items():
        if probability != current_activity:
            activity_keyboard.insert(InlineKeyboardButton(button_and_text[1], callback_data=button_and_text[0]))
        else:
            text = button_and_text[2]
    return activity_keyboard, text


def new_member_keyboard(user_id):
    nm_keyboard = InlineKeyboardMarkup()
    for k, v in sorted(verified_dict.items(), key=lambda x: random()):
        nm_keyboard.add(InlineKeyboardButton(v, callback_data=f'{k}={user_id}'))
    return nm_keyboard


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
    st_keyboard.add(InlineKeyboardButton('Когда новая серия или глава?', switch_inline_query='when'))
    st_keyboard.add(InlineKeyboardButton('Cтикеры', callback_data='stickers'))
    st_keyboard.add(InlineKeyboardButton('Сделать и отправить мем', callback_data='create_memes'))
    if its_admin:
        st_keyboard.add(InlineKeyboardButton('Отправить сообщение в чат', callback_data='send'))
    return st_keyboard


def stickers_keyboard(its_admin, stickers):
    stk_keyboard = InlineKeyboardMarkup(row_width=2)
    for k, v in stickers.items():
        stk_keyboard.insert(InlineKeyboardButton(k, url=v))
    if its_admin:
        stk_keyboard.row(InlineKeyboardButton('Добавить сюда стикерпак', callback_data='add_stickers'),
                         InlineKeyboardButton('Удалить отсюда стикерпак', callback_data='del_stickers'))
    stk_keyboard.add(InlineKeyboardButton('Назад', callback_data='cancel'))
    return stk_keyboard


def del_stickers_keyboard(stickers):
    dstk_keyboard = InlineKeyboardMarkup()
    for k in stickers:
        dstk_keyboard.add(InlineKeyboardButton(k, callback_data=k))
    dstk_keyboard.add(InlineKeyboardButton('Отмена', callback_data='cancel'))
    return dstk_keyboard


def memes_send(file_id):
    return InlineKeyboardMarkup().add(InlineKeyboardButton('Отправить', switch_inline_query=f'send_memes={file_id}'))


def cancel_button():
    return InlineKeyboardMarkup().add(InlineKeyboardButton('Отмена', callback_data='cancel'))
