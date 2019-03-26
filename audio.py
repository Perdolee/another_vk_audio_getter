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
    key = input("Enter authentication code: ")
    remember_device = True

    return key, remember_device


def captcha_handler(captcha):
    key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()
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

    choice = input('Enter 0 to download your audios or write user_id or group_id without "id" to download other people music: ')

    user_id = vk.users.get()[0]['id'] if choice == '0' else choice

    for audio in vk_audio.get_iter(user_id):
        artist = audio['artist'].replace('/', '')
        title = audio['title'].replace('/', '')
        url = audio['url']
        file_name = '/'.join((DOWNLOAD_DIR, '{} - {}.mp3'.format(artist, title)))
        if not os.path.isfile(file_name):
            response = requests.get(url, stream=True)
            print('Downloading: {}'.format(file_name), sep=' ')
            try:
                with open(file_name, 'wb') as f:
                    shutil.copyfileobj(response.raw, f)
            except Exception as error_msg:
                print(error_msg)
            print('OK')

if __name__ == '__main__':
    main()
