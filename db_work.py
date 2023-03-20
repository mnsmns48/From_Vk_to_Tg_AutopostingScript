import sqlite3, vk_api
from datetime import datetime

from config import load_config
from colorama import init
from colorama import Fore, Style

config = load_config(".env")
init()


def find_user_func(data):
    try:
        chars = "☎️,►,+,(,),-,+,!,.,:,[,],а,б,в,г,д,е,ё,ж,з,и,й,к,л,м,н,о,п,р,с,т,у,ф,х,ц,ч,ш,щ,ы,ь,ъ,э,ю,я,А,Б,В,Г," \
                "Д,Е,Ё,Ж,З,И,Й,К,Л,М,Н,О,П,Р,С,Т,У,Ф,Х,Ц,,Ч,Ш,Щ,Ы,Э,Ю,Я,/,', "
        text = str(data.get('text').translate(str.maketrans('', '', chars)).split())
        index = text.find("978")
        if index > 1:
            number = str(7)
            while len(number) != 11:
                number += text[index]
                index += 1
            if number:
                return number
        else:
            return None
    except IndexError as error:
        print("ERROR!", error)
        return None


def read_people_base(arg: str, arg2: str, arg3: int):
    try:
        sqlite_connection = sqlite3.connect('base_id')
        cursor = sqlite_connection.cursor()
        sqlite_select_query = f"SELECT {arg} FROM PEOPLE WHERE {arg2}={arg3}"
        cursor.execute(sqlite_select_query)
        record = cursor.fetchone()
        return record[0]
    except TypeError:
        return None


def write_people_base(user_id: int, phone_number: int):
    sqlite_connection = sqlite3.connect('base_id', check_same_thread=False)
    cursor = sqlite_connection.cursor()
    cursor.execute('INSERT INTO PEOPLE (user_id, full_name, phone_number) VALUES (?, ?, ?)',
                   (user_id, _get_username(user_id), phone_number))
    sqlite_connection.commit()


def _def_signer_id_func(data):
    signer_id = data.get('signer_id')
    if signer_id:
        _fnd_user_ph = find_user_func(data)
        if _fnd_user_ph:
            _fnd_user_id = read_people_base('USER_ID', 'PHONE_NUMBER', int(_fnd_user_ph))
            if _fnd_user_id:
                return signer_id
            else:
                print(
                    Fore.GREEN + f"{data.get('id')} Write: {_fnd_user_ph} "
                                 f"{_get_username(signer_id)} VK ID:{signer_id}" + Style.RESET_ALL)
                write_people_base(signer_id, int(_fnd_user_ph))
                return signer_id
        else:
            return signer_id
    else:
        _fnd_user_ph = find_user_func(data)
        if _fnd_user_ph:
            _fnd_user_id = read_people_base('USER_ID', 'PHONE_NUMBER', int(_fnd_user_ph))
            if _fnd_user_id:
                signer_id = _fnd_user_id
                print(Fore.RED, data.get('id'), 'assigned to anonymous ID from DB',
                      read_people_base('FULL_NAME', 'USER_ID', int(_fnd_user_id)) + Style.RESET_ALL)
                return signer_id
            else:
                signer_id = 'Anonymously'
                return signer_id
        else:
            signer_id = 'Anonymously'
            return signer_id


def check_post(post):
    try:
        sqlite_connection = sqlite3.connect('base_id', check_same_thread=False)
        cursor = sqlite_connection.cursor()
        sqlite_select_query = f"SELECT POST FROM POSTS WHERE POST={post}"
        cursor.execute(sqlite_select_query)
        answer = cursor.fetchone()
        return answer[0]
    except TypeError:
        return None


def write_post_data(post_id, text, user_id, time):
    sqlite_connection = sqlite3.connect('base_id', check_same_thread=False)
    cursor = sqlite_connection.cursor()
    cursor.execute('INSERT INTO POSTS (POST, TEXT, USER_ID, TIME) VALUES (?, ?, ?, ?)',
                   (post_id, text, user_id,
                    datetime.fromtimestamp(time).strftime('%d-%m-%Y %H:%M:%S')))
    sqlite_connection.commit()
    print('writen post:', post_id)


def _get_username(user_id):
    session = vk_api.VkApi(token=config.tg_bot.vk_api_token)
    username = session.method('users.get', {'user_id': user_id})[0]
    return ' '.join((username['first_name'], username['last_name']))
