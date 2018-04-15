#!/usr/bin/env python3

import shutil
import time
import getpass
import requests
import os.path
import vk_api
from vk_api.audio import VkAudio

DOWNLOAD_DIR = './download'

def main():
    login, password = input('Login: '), getpass.getpass()

    vk_session = vk_api.VkApi(login, password)
    vk = vk_session.get_api()

    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    vkaudio = VkAudio(vk_session)

    id = vk.users.get()[0]['id']
    audios = vkaudio.get(owner_id=id)

    for audio in audios:
        artist = audio['artist'].replace('/','')
        title = audio['title'].replace('/','')
        url = audio['url']

        file_name = '/'.join((DOWNLOAD_DIR, '{} - {}.mp3'.format(artist, title)))
        if not os.path.isfile(file_name):
            response = requests.get(url, stream=True)
            print('Downloading: {}'.format(file_name))
            with open(file_name, 'wb') as f:
                shutil.copyfileobj(response.raw, f)

            print('OK')
            time.sleep(2)


if __name__ == '__main__':
    main()
