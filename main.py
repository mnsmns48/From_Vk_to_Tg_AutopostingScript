import requests, json
import vk_api
from config import load_config

config = load_config(".env")
session = vk_api.VkApi(token=config.tg_bot.vk_api_token)
vk = session.get_api()


class Posting:
    def __init__(self):
        self.group_id = None

    def repost(self, data):
        self.group_id = data['copy_history'][0]['text']


def write_last_post_id(text):
    with open("last_post.txt", "w") as file:
        file.write(text)


def read_last_post_id():
    f = open('last_post.txt', 'r')
    for line in f:
        return int(line)


def connect(count):
    r = requests.get('https://api.vk.com/method/wall.get',
                     params={
                         'access_token': config.tg_bot.vk_token,
                         'v': 5.131,
                         'domain': config.tg_bot.vk_domain,
                         'count': count,
                         'offset': 0
                     })

    return r.json()['response']['items']


def new_post_list(data):
    posts = []
    for i in range(len(data)):
        posts.append(data[i]['id'])
    last_post = read_last_post_id()
    item = posts.index(last_post)
    del posts[item:]
    print(f'Последний опубликованный пост № {last_post}')
    if list(reversed(posts)):
        print('Посты, готовящиеся к публикации: ', *list(reversed(posts)))
    return list(reversed(posts))


def main():
    posting_list = connect(config.tg_bot.amount_post_list)
    new_post_count = len(new_post_list(posting_list))
    print(f'Количество новых постов: {new_post_count}')
    for n in range(-28, -27, -1):
        post = Posting()
        print(post.repost(posting_list))


if __name__ == '__main__':
    main()
