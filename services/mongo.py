from bson.objectid import ObjectId

from motor.motor_asyncio import AsyncIOMotorClient

import config


sign_in = f'mongodb+srv://{config.username}:' \
          f'{config.password}@cluster0-habpf.mongodb.net/test?retryWrites=true&w=majority'

client = AsyncIOMotorClient(sign_in)

collection = client.marco_bot['Telegram']

db_dict = {'messages': config.messages,
           'admins_panel': config.admins_panel,
           'new_chat_members': config.new_chat_members}


async def find(key):
    data = await collection.find_one({'_id': ObjectId(db_dict[key])})
    return data


async def update(key, data):
    await collection.find_one_and_update({'_id': ObjectId(db_dict[key])}, data)
