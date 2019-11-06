import textwrap

from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw


def prepare_text(top_string, bottom_string):
    strings = []
    for string in top_string, bottom_string:
        if len(string) > 45:
            string = string.strip()
            strings.append('\n'.join(textwrap.wrap(string, width=45)))
        else:
            strings.append(string)
    top_string, bottom_string = strings
    return top_string, bottom_string



# исходник этого куска https://github.com/danieldiekmeier/memegenerator
# он немного отредактирован под себя, мне лень его переписывать заново
def make_meme(topString, bottomString, filename, new_file):
    if len(topString) > 45:
        topString = topString.splitlines()
    if len(bottomString) > 45:
        bottomString = bottomString.splitlines()

    img = Image.open(filename)
    imageSize = img.size

    # find biggest font size that works
    fontSize = int(imageSize[1] / 5)

    font = ImageFont.truetype("fonts/Lobster.ttf", fontSize)
    topTextSize = font.getsize(topString)
    bottomTextSize = font.getsize(bottomString)

    while topTextSize[0] > imageSize[0] - 20 or bottomTextSize[0] > imageSize[0] - 20:
        fontSize = fontSize - 1
        font = ImageFont.truetype("fonts/Lobster.ttf", fontSize)
        topTextSize = font.getsize(topString)
        bottomTextSize = font.getsize(bottomString)

    # find top centered position for top text
    topTextPositionX = (imageSize[0] / 2) - (topTextSize[0] / 2)
    topTextPositionY = 0
    topTextPositionYString2 = topTextPositionY + fontSize
    topTextPosition = (topTextPositionX, topTextPositionY)


    # find bottom centered position for bottom text
    bottomTextPositionX = (imageSize[0] / 2) - (bottomTextSize[0] / 2)
    bottomTextPositionY = imageSize[1] / 1.05 - bottomTextSize[1] / 1.05
    bottomTextPositionYString2 = bottomTextPositionY - fontSize
    bottomTextPosition = (bottomTextPositionX, bottomTextPositionY)


    draw = ImageDraw.Draw(img)

    # draw outlines
    # there may be a better way
    outlineRange = int(fontSize / 15)

    if isinstance(topString, list):
        topString, topString2 = topString
        topTextSizeString2 = font.getsize(topString2)
        topTextPositionXString2 = (imageSize[0] / 2) - (topTextSizeString2[0] / 2)
        topTextPositionString2 = (topTextPositionXString2, topTextPositionYString2)
        for x in range(-outlineRange, outlineRange + 1):
            for y in range(-outlineRange, outlineRange + 1):
                draw.text((topTextPositionString2[0] + x, topTextPositionString2[1] + y), topString2, (0, 0, 0),
                          font=font, align='center')
                draw.text((topTextPosition[0] + x, topTextPosition[1] + y), topString, (0, 0, 0), font=font,
                          align='center')
        draw.text(topTextPositionString2, topString2, (255, 255, 255), font=font)
        draw.text(topTextPosition, topString, (255, 255, 255), font=font)
    elif topString != '*':
        for x in range(-outlineRange, outlineRange + 1):
            for y in range(-outlineRange, outlineRange + 1):
                draw.text((topTextPosition[0] + x, topTextPosition[1] + y), topString, (0, 0, 0), font=font,
                          align='center')
        draw.text(topTextPosition, topString, (255, 255, 255), font=font)


    if isinstance(bottomString, list):
        bottomString, bottomString2 = bottomString
        bottomTextSizeString2 = font.getsize(bottomString2)
        bottomTextPositionY = imageSize[1] / 1.05 - bottomTextSize[1] / 1.05
        bottomTextPositionXString2 = (imageSize[0] / 2) - (bottomTextSizeString2[0] / 2)
        bottomTextPosition = (bottomTextPositionX, bottomTextPositionYString2)
        bottomTextPositionString2 = (bottomTextPositionXString2, bottomTextPositionY)
        for x in range(-outlineRange, outlineRange + 1):
            for y in range(-outlineRange, outlineRange + 1):
                draw.text((bottomTextPositionString2[0] + x, bottomTextPositionString2[1] + y), bottomString2,
                          (0, 0, 0), font=font, align='center')
                draw.text((bottomTextPosition[0] + x, bottomTextPosition[1] + y), bottomString, (0, 0, 0), font=font,
                          align='center')
        draw.text(bottomTextPositionString2, bottomString2, (255, 255, 255), font=font)
        draw.text(bottomTextPosition, bottomString, (255, 255, 255), font=font)
    elif bottomString != '*':
        for x in range(-outlineRange, outlineRange + 1):
            for y in range(-outlineRange, outlineRange + 1):
                draw.text((bottomTextPosition[0] + x, bottomTextPosition[1] + y), bottomString, (0, 0, 0), font=font,
                          align='center')
        draw.text(bottomTextPosition, bottomString, (255, 255, 255), font=font)

    img.save(new_file)
