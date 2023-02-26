import time

import requests, time
from config import load_config
from db_work import _def_signer_id_func

config = load_config(".env")


def connect(offset):
    r = requests.get('https://api.vk.com/method/wall.get',
                     params={
                         'access_token': config.tg_bot.vk_token,
                         'v': 5.131,
                         'owner_id': config.tg_bot.owner_id,
                         'count': 1,
                         'offset': offset
                     })

    return r.json()['response']['items']


i = 26000 #438136
while True:
    try:
        data = connect(i)
        signer_id = _def_signer_id_func(data[0])
        i += 1
        time.sleep(1)
    except KeyboardInterrupt:
        print('Скрипт остановлен')