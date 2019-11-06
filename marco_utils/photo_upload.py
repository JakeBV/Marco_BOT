import requests

def upload_photo(photo):
    with open(f'images_with_text/{photo}', 'rb') as f:
        return requests.post('https://telegra.ph/upload',
                             files={'file': ('file', f, 'image/png')},
                             ).json()[0]['src']