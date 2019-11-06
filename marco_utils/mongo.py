import urllib.parse
import configparser
from bson.objectid import ObjectId

import motor.motor_asyncio


config = configparser.ConfigParser()
config.read('config.ini')


username = urllib.parse.quote_plus(config['MONGO']['username'])
password = urllib.parse.quote_plus(config['MONGO']['password'])


sign_in = f'mongodb+srv://{username}:{password}@cluster0-habpf.mongodb.net/test?retryWrites=true&w=majority'

client = motor.motor_asyncio.AsyncIOMotorClient(sign_in)

collection = client.marco_bot['Telegram']


db_dict = {'messages': config['MONGO']['messages'],
           'admins_panel': config['MONGO']['admins_panel'],
           'new_chat_members': config['MONGO']['new_chat_members']}


async def find(key):
    data = await collection.find_one({'_id': ObjectId(db_dict[key])})
    return data



async def update(key, data):
    await collection.find_one_and_update({'_id': ObjectId(db_dict[key])}, data)




