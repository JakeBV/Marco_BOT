from re import compile
from re import findall

from aiogram.utils.exceptions import ChatNotFound

import misc


async def search_entities(entities, text):
    for ent in entities:
        if ent['type'] in ('url', 'email', 'text_link'):
            return True
        elif ent['type'] == 'mention':
            mentions = findall(compile('@\w{3,50}'), text)
            for mention in mentions:
                try:
                    await misc.bot.get_chat(mention)
                    return True
                except ChatNotFound:
                    continue


def search_urls_in_keyboard(inline_keyboard):
    buttons = []
    for row in inline_keyboard:
        buttons.extend([button.url for button in row if button.url is not None])
    return buttons
