from os import path
from random import choices
from time import time

from aiogram import types
from aiogram.dispatcher.filters.filters import BoundFilter

from config import angel
from config import translator
from services import keyboards
from services import mongo
from utils import json_worker


class IsAngel(BoundFilter):
    key = 'is_angel'

    def __init__(self, is_angel):
        self.is_angel = is_angel

    async def check(self, message):
        return message.from_user.id == angel and angel in [user.id for user in message.new_chat_members]


class IsNewUser(BoundFilter):
    key = 'is_new_user'

    def __init__(self, is_new_user):
        self.is_new_user = is_new_user

    async def check(self, message):
        get_users_info = (await mongo.find('new_chat_members'))['new_chat_members'].get(f'{message.from_user.id}')
        if (get_users_info is None) or (time() - get_users_info['join_time'] < 86400):
            return True


class IsSpam(BoundFilter):
    key = 'is_spam'

    def __init__(self, is_spam):
        self.is_spam = is_spam

    async def check(self, message: types.Message):
        return message.entities or message.caption_entities or message.reply_markup


class IsVerification(BoundFilter):
    key = 'is_verification'

    def __init__(self, is_verification):
        self.is_verification = is_verification

    async def check(self, callback_query: types.CallbackQuery):
        return callback_query.data.split('=')[0] in keyboards.verified_dict


class IsAntispamSettings(BoundFilter):
    key = 'is_antispam_settings'

    def __init__(self, is_antispam_settings):
        self.is_antispam_settings = is_antispam_settings

    async def check(self, callback_query):
        return callback_query.data.split('=')[0] in ('disable_antispam', 'block')


class IsReplyText(BoundFilter):
    key = 'is_reply_text'

    def __init__(self, is_reply_text):
        self.is_reply_text = is_reply_text

    async def check(self, message: types.Message):
        if message.reply_to_message:
            return message.reply_to_message.text or message.reply_to_message.caption


class IsUkrainian(BoundFilter):
    key = 'is_ukrainian'

    def __init__(self, is_ukrainian):
        self.is_ukrainian = is_ukrainian

    async def check(self, message: types.Message):
        return translator.detect(message.text).lang == 'uk'


class IsActivitySettings(BoundFilter):
    key = 'is_activity_settings'

    def __init__(self, is_activity_settings):
        self.is_activity_settings = is_activity_settings

    async def check(self, callback_query: types.CallbackQuery):
        return callback_query.data in keyboards.activities_dict


class IsImitationTalk(BoundFilter):
    key = 'is_imitation_talk'

    def __init__(self, is_imitation_talk):
        self.is_imitation_talk = is_imitation_talk

    async def check(self, message):
        weights = json_worker.read_json(path.join('data', 'weights.json'))
        return choices([True, False], weights=weights)[0]


class IsSendMemes(BoundFilter):
    key = 'is_send_memes'

    def __init__(self, is_send_memes):
        self.is_send_memes = is_send_memes

    async def check(self, inline_query: types.InlineQuery):
        return (inline_query.query.split('=')[0] == 'send_memes') and (len(inline_query.query.split('=')) == 2)
