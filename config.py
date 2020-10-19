from urllib.parse import quote_plus
from configparser import ConfigParser
from os import path

from googletrans import Translator

translator = Translator()

config = ConfigParser()
config.read(path.join('data', 'config.ini'))

token = config['BOT']['token']
snk_chat = int(config['BOT']['chat'])
angel = int(config['BOT']['angel'])
me = int(config['BOT']['me'])

username = quote_plus(config['MONGO']['username'])
password = quote_plus(config['MONGO']['password'])
admins_panel = config['MONGO']['admins_panel']
messages = config['MONGO']['messages']
new_chat_members = config['MONGO']['new_chat_members']
