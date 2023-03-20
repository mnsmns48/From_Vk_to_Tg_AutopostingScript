import requests, json, sqlite3

from attachments import scrape_data
from config import load_config
from datetime import datetime

from db_work import check_post, _def_signer_id_func

config = load_config(".env")


def connect(count):
    r = requests.get('https://api.vk.com/method/wall.get',
                     params={
                         'access_token': config.tg_bot.vk_token,
                         'v': 5.131,
                         'owner_id': config.tg_bot.owner_id,
                         'count': count,
                         'offset': 0
                     })

    return r.json()['response']['items']


# data = connect(200)
# low = []
# for i in range(len(data)):
#     find = check_post(data[i].get('id'))
#     if find:
#         continue
#     else:
#         low.append(data[i].get('id'))
# print(low)
# print(len(low))
# def wr(post):
#     signer_id = _def_signer_id_func(post)
#     sqlite_connection = sqlite3.connect('base_id', check_same_thread=False)
#     cursor = sqlite_connection.cursor()
#     cursor.execute('INSERT INTO POSTS (POST, TEXT, USER_ID, TIME) VALUES (?, ?, ?, ?)',
#                    (post.get('id'), post.get('text'), signer_id,
#                     datetime.fromtimestamp(post['date']).strftime('%d-%m-%Y %H:%M:%S')))
#     sqlite_connection.commit()
#
#
# for i in data:
#     wr(scrape_data(i))


print(check_post(542449))
