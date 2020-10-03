import requests

def upload_photo(b):
    return requests.post('https://telegra.ph/upload', files={'file': ('file', b, 'image/png')}).json()[0]['src']