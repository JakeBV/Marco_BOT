from aiogram import Bot
from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from config import token
from services import filters

custom_filters = [filters.IsActivitySettings, filters.IsAngel, filters.IsAntispamSettings, filters.IsImitationTalk,
                  filters.IsNewUser, filters.IsReplyText, filters.IsSendMemes, filters.IsSpam, filters.IsUkrainian,
                  filters.IsVerification]

bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
for custom_filter in custom_filters:
    dp.filters_factory.bind(custom_filter)
