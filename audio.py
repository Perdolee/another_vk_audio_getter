#!/usr/bin/env python3

import getpass
import os.path
import re
import shutil
import time

import requests
import vk_api
from vk_api.audio import VkAudio

DOWNLOAD_DIR = './download'
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)


def auth_handler():
    """ При двухфакторной аутентификации вызывается эта функция.
    """

    # Код двухфакторной аутентификации
    key = input("Enter authentication code: ")
    # Если: True - сохранить, False - не сохранять.
    remember_device = True

    return key, remember_device


def captcha_handler(captcha):
    """ При возникновении капчи вызывается эта функция и ей передается объект
        капчи. Через метод get_url можно получить ссылку на изображение.
        Через метод try_again можно попытаться отправить запрос с кодом капчи
    """

    key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()

    # Пробуем снова отправить запрос с капчей
    return captcha.try_again(key)


def main():
    login, password = input('Login: '), getpass.getpass()

    vk_session = vk_api.VkApi(login, password, auth_handler=auth_handler, captcha_handler=captcha_handler)
    vk = vk_session.get_api()

    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    vk_audio = VkAudio(vk_session)

    user_id = vk.users.get()[0]['id']
    audios = []
    try:
        print('Getting audio playlist, please wait')
        for track in vk_audio.get_iter(user_id):
            audios.append(track)
    except AttributeError as error_msg:
        print(error_msg)
        print('Please upgrade vk_api library. Use: "pip install vk_api --upgrade --user"')
        return

    for audio in audios:
        artist = audio['artist'].replace('/', '')
        title = audio['title'].replace('/', '')
        url = audio['url']
        file_name = '/'.join((DOWNLOAD_DIR, '{} - {}.mp3'.format(artist, title)))
        re.sub('[^\w\-_.]', '_', file_name)
        if not os.path.isfile(file_name):
            response = requests.get(url, stream=True)
            print('Downloading: {}'.format(file_name), sep=' ')
            try:
                with open(file_name, 'wb') as f:
                    shutil.copyfileobj(response.raw, f)
            except Exception as error_msg:
                print(error_msg)
            print('OK')
            time.sleep(2)


if __name__ == '__main__':
    main()
