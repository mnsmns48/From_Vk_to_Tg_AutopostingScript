import vk_api, requests, json, time, os, shutil
from datetime import datetime
from config import load_config
from tqdm import tqdm

config = load_config(".env")
session = vk_api.VkApi(token=config.tg_bot.vk_api_token)
vk = session.get_api()


def post_to_admin(text):
    request_url = "https://api.telegram.org/bot" + config.tg_bot.bot_token + "/sendMessage"
    params = {"chat_id": config.tg_bot.admin,
              "text": text}
    requests.post(request_url, params=params)


def scrape_repost_photos(data, image_list):
    if len(data['copy_history'][0]['attachments']) > 0:
        if 'photo' in data['copy_history'][0]['attachments'][0]:
            count_att = len(data['copy_history'][0]['attachments'])
            for i in range(count_att):
                if 'photo' in data['copy_history'][0]['attachments'][i]:
                    image_list.append(f'x_image/{data["id"]}_{i}.jpg')
                    photo = requests.get(data['copy_history'][0]['attachments'][i]['photo']['sizes'][-1]['url'])
                    with open(f'x_image/{data["id"]}_{i}.jpg', 'wb') as fd:
                        for chunk in photo.iter_content(50000):
                            fd.write(chunk)
                            time.sleep(3)
            return image_list
        if 'doc' in data['copy_history'][0]['attachments'][0]:
            count_att = len(data['copy_history'][0]['attachments'])
            for i in range(count_att):
                if 'photo' in data['copy_history'][0]['attachments'][i]:
                    image_list.append(f'x_image/{data["id"]}_{i}.jpg')
                    photo = requests.get(
                        data['copy_history'][0]['attachments'][i]['doc']['preview']['photo']['sizes'][-1]['src'])
                    with open(f'x_image/{data["id"]}_{i}.jpg', 'wb') as fd:
                        for chunk in photo.iter_content(50000):
                            fd.write(chunk)
                            time.sleep(3)
            return image_list
        else:
            return image_list


def scrape_normalposting_photos(data, image_list):
    if len(data['attachments']) > 0:
        if 'photo' in data['attachments'][0]:
            for i in range(len(data['attachments'])):
                if 'photo' in data['attachments'][i]:
                    image_list.append(f'x_image/{data["id"]}_{i}.jpg')
                    photo = requests.get(data['attachments'][i]['photo']['sizes'][-1]['url'])
                    with open(f'x_image/{data["id"]}_{i}.jpg', 'wb') as fd:
                        for chunk in photo.iter_content(50000):
                            fd.write(chunk)
                            time.sleep(3)
            return image_list
        if 'doc' in data['attachments'][0]:
            for i in range(len(data['attachments'])):
                if 'photo' in data['attachments'][i]:
                    image_list.append(f'x_image/{data["id"]}_{i}.jpg')
                    photo = requests.get(
                        data['attachments'][i]['doc']['preview']['photo']['sizes'][-1]['src'])
                    time.sleep(2)
                    with open(f'x_image/{data["id"]}_{i}.jpg', 'wb') as fd:
                        for chunk in photo.iter_content(50000):
                            fd.write(chunk)
                            time.sleep(3)
            return image_list
        else:
            return image_list


def send_with_media(data, images, caption, photo='photo'):
    request_url = "https://api.telegram.org/bot" + config.tg_bot.bot_token + "/sendMediaGroup"
    files = {f'post_name{item}': open(f'{images[item]}', 'rb') for item in range(len(images))}
    caption = caption
    list_attach = [
        {"type": photo, "media": "attach://post_name0", "caption": caption, "parse_mode": 'HTML'}]
    if len(images) >= 2:
        for item in range(len(images) - 1):
            list_attach.append({"type": photo, "media": f"attach://post_name{item + 1}"})
    media = json.dumps(list_attach)
    params = {"chat_id": config.tg_bot.tg_chat,
              "media": media,
              "disable_notification": config.tg_bot.notification}
    result = requests.post(request_url, params=params, files=files)
    if result.status_code == 200:
        time_now = datetime.fromtimestamp(time.mktime(datetime.now().timetuple())).strftime('%H:%M:%S')
        admin_message = f"{data['id']}, {result.ok}, Фотографии:, {len(list_attach)}, send_with_media, {time_now}"
        print(admin_message)
        post_to_admin(admin_message)
        with open("last_post.txt", "w") as file:
            file.write(str(data['id']))
            file.close()


def send_only_text(data, text):
    try:
        video_owner_id = str(data['attachments'][0]['video']['owner_id'])
        video_id = str(data['attachments'][0]['video']['id'])
        if 'video' in data['attachments'][0]:
            link = f'\n\n<a href="https://vk.com/video{video_owner_id}_{video_id}">→→→→→ Видео ссылка ←←←←←</a>'
        else:
            link = ''
    except (IndexError, KeyError):
        link = ''
    request_url = "https://api.telegram.org/bot" + config.tg_bot.bot_token + "/sendMessage"
    if len(data['attachments']) > 0:
        params = {"chat_id": config.tg_bot.tg_chat,
                  "text": text + link,
                  "parse_mode": 'HTML',
                  "disable_web_page_preview": False,
                  "disable_notification": config.tg_bot.notification}
    else:
        params = {"chat_id": config.tg_bot.tg_chat,
                  "text": text + link,
                  "parse_mode": 'HTML',
                  "disable_web_page_preview": True,
                  "disable_notification": config.tg_bot.notification}
    result = requests.post(request_url, params=params)
    if result.status_code == 200:
        time_now = datetime.fromtimestamp(time.mktime(datetime.now().timetuple())).strftime('%H:%M:%S')
        admin_message = f"{data['id']}, {result.ok}, Фотографии: 0, send_only_text, {time_now}"
        print(admin_message)
        post_to_admin(admin_message)
        with open("last_post.txt", "w") as file:
            file.write(str(data['id']))
            file.close()


class Repost:
    def __init__(self, data):
        self.data = data
        self._images = None
        self.image_list = []
        self.id = data['id']
        try:
            self.signer_id = _get_username(data['copy_history'][0]['signer_id'])
        except KeyError:
            self.signer_id = 'Anonymously'
        self.txt = data['copy_history'][0]['text']
        self.paid = '<i>          Платная реклама</i>' if data.get('marked_as_ads') else ''
        self._group_id = data['copy_history'][0]['from_id']
        self._group_name = session.method('groups.getById', {'group_id': -self._group_id})[0]['name']
        self.repost_group = f'<a href="https://vk.com/public{self._group_id}">{self._group_name}</a>'
        try:
            self.url_sign = 'vk.com/id' + str(data.get(data['copy_history'][0]['signer_id']))
        except KeyError:
            self.url_sign = ''
        self.postbot = 'предложить новость @pgtlenino_bot'
        self.photo = 'photo'
        if self.signer_id != 'Anonymously':
            self.text = f'<b> ↑ ↑ ↑ ↑ Р Е П О С Т ↓ ↓ ↓ ↓</b>\n{self.repost_group}\n' + \
                    self.txt + f'\n<a href="{self.url_sign}">{self.signer_id}</a>\n{self.paid}\n{self.postbot}'
        else:
            self.text = f'<b> ↑ ↑ ↑ ↑ Р Е П О С Т ↓ ↓ ↓ ↓</b>\n{self.repost_group}\n' + \
                    self.txt + f'\nАнонимно\n{self.paid}\n{self.postbot}'

    def send_to_tg(self):
        self._images = scrape_repost_photos(self.data, image_list=[])
        if self.data['copy_history'][0]['attachments'] == [] or 'video' in self.data['copy_history'][0]['attachments'][
            0]:
            send_only_text(self.data, self.text)
        else:
            if len(self.data['copy_history'][0]['text']) < 950:
                send_with_media(self.data, self._images, self.text, 'photo')
                time.sleep(3)
            else:
                send_with_media(self.data, self._images, '', 'photo')
                send_only_text(self.data, self.text)


class NormalPosting:
    def __init__(self, data):
        self.data = data
        self._images = None
        self.image_list = []
        self.id = data['id']
        try:
            self.signer_id = _get_username(data['signer_id'])
        except KeyError:
            self.signer_id = 'Anonymously'
        self.txt = data['text']
        try:
            self.url_sign = 'vk.com/id' + str(data.get(data['signer_id']))
        except KeyError:
            self.url_sign = ''
        self.postbot = 'предложить новость @pgtlenino_bot'
        self.photo = 'photo'
        if self.signer_id != 'Anonymously':
            self.text = self.txt + f'\n\n<a href="{self.url_sign}">{self.signer_id}</a>\n{self.postbot}'
        else:
            self.text = self.txt + f'\n\nАнонимно\n{self.postbot}'

    def send_to_tg(self):
        self._images = scrape_normalposting_photos(self.data, image_list=[])
        if self.data['attachments'] == [] or 'video' in self.data['attachments'][0]:
            send_only_text(self.data, self.text)
        else:
            if len(self.data['text']) < 950:
                send_with_media(self.data, self._images, self.text, 'photo')
                time.sleep(3)
            else:
                send_with_media(self.data, self._images, '', 'photo')
                send_only_text(self.data, self.text)


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


def _get_username(user_id):
    username = session.method('users.get', {'user_id': user_id})[0]
    return ' '.join((username['first_name'], username['last_name']))


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
    while True:
        data_list = connect(config.tg_bot.amount_post_list)
        new_post_count = len(new_post_list(data_list))
        print(f'Количество новых постов: {new_post_count}')
        unpublished = []
        for n in range(new_post_count - 1, -1, -1):
            unpublished.append(data_list[n])
        for i in range(len(unpublished)):
            if 'copy_history' in unpublished[i]:
                repost = Repost(unpublished[i])
                repost.send_to_tg()
            else:
                post = NormalPosting(unpublished[i])
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


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Скрипт остановлен')
