import requests, time, os, shutil
from tqdm import tqdm
from config import load_config

from db_work import _def_signer_id_func, _get_username
from attachments import scrape_photos, send_text, send_media, scrape_data

config = load_config(".env")
data_list = list()


class Posting:
    def __init__(self, data):
        self._char_exceed = None
        self._video_key = None
        self._images = None
        self.data = data
        self.id = self.data['id']
        self.paid = '<i>          Платная реклама</i>' if self.data.get('marked_as_ads') else ' '
        self.txt = self.data.get('text')
        self._att_key = 1 if self.data.get('attachments') else 0
        self.repost = self.data.get('repost_text') if self.data.get('repost_text') else ' '
        if self._att_key == 1:
            self._video_key = 1 if self.data['attachments'][0].get('type') == 'video' else 0
        self.signer_id = _def_signer_id_func(self.data)
        if self.signer_id == 'Anonymously':
            self.message = self.txt + f'\n          Анонимно'
        elif self._video_key == 1:
            self.message = self.txt
        else:
            self.signer_fullname = _get_username(self.signer_id)
            self.signer_url = 'vk.com/id' + str(self.signer_id)
            self.message = f"{self.repost}\n{self.txt}\n<a href='{self.signer_url}'>          {self.signer_fullname}</a>\n{self.paid}"

    def send_to_tg(self):
        self._char_exceed = True if len(self.message) < 1024 else False
        self._images = scrape_photos(self.data)
        if self._att_key == 0 or self._video_key == 1:
            send_text(self.data, self.message)
        else:
            if self._char_exceed:
                send_media(self.data, self._images, self.message, self._char_exceed)
                time.sleep(3)
            else:
                send_media(self.data, self._images, self.message, self._char_exceed)
                send_text(self.data, self.message)
                time.sleep(3)


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
                         'owner_id': config.tg_bot.owner_id,
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


if __name__ == '__main__':
    try:
        while True:
            big_data = connect(config.tg_bot.amount_post_list)
            for i in range(len(big_data)):
                data_list.append(scrape_data(big_data[i]))
            new_post_count = len(new_post_list(data_list))
            print(f'Количество новых постов: {new_post_count}')
            unpublished = []
            for n in range(new_post_count - 1, -1, -1):
                unpublished.append(data_list[n])
            for i in range(len(unpublished)):
                post = Posting(unpublished[i])
                post.send_to_tg()
            if len(os.listdir('x_image')) > 0:
                path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'x_image')
                shutil.rmtree(path)
                os.mkdir('x_image')
            else:
                pass
            exp_list = [i for i in range(0, 600)]
            for i in tqdm(exp_list):
                time.sleep(1)
    except KeyboardInterrupt:
        print('Скрипт остановлен')
