from aiogram.utils.helper import Helper, HelperMode, ListItem


class VerificationStates(Helper):
    mode = HelperMode.snake_case

    S1_NOT_VERIFICATION = ListItem()
    S2_VERIFICATION = ListItem()
    S3_FULL_PARTICIPANT = ListItem()
    S4_CREATE_MEMES = ListItem()
    S5_SEND_MESSAGE = ListItem()
    S6_START = ListItem()
