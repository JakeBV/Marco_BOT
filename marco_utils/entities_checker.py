import re

async def search_entities(bot, entities, text):
    for ent in entities:
        if ent['type'] in ('url', 'email', 'text_link'):
            return True
        elif ent['type'] == 'mention':
            chats = re.findall(re.compile('@\w{3,50}'), text)
            for chat in chats:
                try:
                    await bot.get_chat(chat)
                    return True
                except:
                    pass

