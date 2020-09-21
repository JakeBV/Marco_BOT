import textwrap

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


def create_image(message, title):
    xH = 1
    xW = len(message) + 3
    if xW > 50:
        text = textwrap.wrap(message, width=50, break_long_words=False)
        xH = len(text) + xH
        xW = 58
        message = '\n'.join(text)
    W, H = 15 * xW, 40 * xH
    background = Image.new('RGB', (W, H), (255, 255, 255))
    font = ImageFont.truetype('fonts/Cambria.ttf', 30)
    draw = ImageDraw.Draw(background)
    w, h = draw.textsize(message, font)
    x = (W - w) / 2
    y = (H - h) / 2
    draw.text((x, y), message, font=font, align="center", fill=0)
    background.save(f'images_with_text/{title}.png')

