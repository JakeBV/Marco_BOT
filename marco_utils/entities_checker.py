import re

async def search_entities(bot, entities, text):
    for ent in entities:
        if ent['type'] in ('url', 'email', 'text_link'):
            return True
        elif ent['type'] == 'mention':
            chat = re.findall(re.compile('@\w{3,50}'), text)[0]
            try:
                await bot.get_chat(chat)
                return True
            except:
                return False

