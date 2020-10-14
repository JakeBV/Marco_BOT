from aiogram.utils.helper import Helper
from aiogram.utils.helper import HelperMode
from aiogram.utils.helper import Item


class VerificationStates(Helper):
    mode = HelperMode.snake_case

    S1_NOT_VERIFICATION = Item()
    S2_VERIFICATION = Item()


class PrivateStates(Helper):
    mode = HelperMode.snake_case

    P1_CREATE_MEMES = Item()
    P2_SEND_MESSAGE = Item()
    P3_ADD_STICKERS = Item()
    P4_DEL_STICKERS = Item()
