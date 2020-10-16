from io import BytesIO
from os import path
from re import search
from textwrap import wrap
from urllib.parse import urlsplit

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from requests import post


def upload_photo(image):
    return post('https://telegra.ph/upload', files={'file': ('file', image, 'image/png')}).json()[0]['src']


def check_validity_stickerpack(text, stickers):
    try:
        stickers_title, stickers_link = text.split('|')
        path = urlsplit(stickers_link.strip()).path
    except ValueError:
        return False
    return (path[:13] == '/addstickers/') and \
           (len(path[13:]) > 3) and bool(search(r"[a-zA-Zа-яА-Я]", stickers_title)) and \
           (stickers_title.strip() not in stickers.keys()) and (stickers_link.strip() not in stickers.values())


def text_to_image(message, message_id):
    rows = len(message.split('\n')) + 1
    columns = len(message) + 3
    if columns > 50:
        text = wrap(message, width=50, break_long_words=False, replace_whitespace=False)
        rows = len(text) + rows
        columns = 58
        message = '\n'.join(text)
    width, height = 15 * columns, 40 * rows
    background = Image.new('RGB', (width, height), (255, 255, 255))
    font = ImageFont.truetype(path.join('fonts', 'Cambria.ttf'), 30)
    draw = ImageDraw.Draw(background)
    w, h = draw.textsize(message, font)
    draw.text(((width - w) / 2, (height - h) / 2), message, font=font, align="center", fill=0)
    image = BytesIO()
    image.name = f'{message_id}.png'
    background.save(image, 'PNG')
    image.seek(0)
    return image
