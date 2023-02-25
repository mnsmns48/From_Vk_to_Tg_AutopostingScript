import sqlite3, vk_api
from config import load_config

config = load_config(".env")


def find_user_func(data):
    try:
        chars = '☎️,►,+,(,),-,+,!,.,:,[,],а,б,в,г,д,е,ё,ж,з,и,й,к,л,м,н,о,п,р,с,т,у,ф,х,ц,ч,ш,щ,ы,ь,ъ,э,ю,я,А,Б,В,Г,' \
                'Д,Е,Ё,Ж,З,И,Й,К,Л,М,Н,О,П,Р,С,Т,У,Ф,Х,Ц,,Ч,Ш,Щ,Ы,Э,Ю,Я, '
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
    except IndexError:
        return None


def read_base(phone_number: int):
    try:
        sqlite_connection = sqlite3.connect('base_id')
        cursor = sqlite_connection.cursor()
        sqlite_select_query = f"SELECT USER_ID FROM MAIN WHERE PHONE_NUMBER={phone_number}"
        cursor.execute(sqlite_select_query)
        record = cursor.fetchone()
        return record[0]
    except TypeError:
        return None


def write_base(user_id: int, phone_number: int):
    sqlite_connection = sqlite3.connect('base_id', check_same_thread=False)
    cursor = sqlite_connection.cursor()
    cursor.execute('INSERT INTO MAIN (user_id, full_name, phone_number) VALUES (?, ?, ?)',
                   (user_id, _get_username(user_id), phone_number))
    sqlite_connection.commit()


def _def_signer_id_func(data):
    print('Начало работы функции _def_signer_id_func')
    signer_id = data.get('signer_id')
    if signer_id:
        print('Пост подписан с id:', _get_username(signer_id))
        _fnd_user_ph = find_user_func(data)
        if _fnd_user_ph:
            print('В посте есть такой телефон:', _fnd_user_ph,
                  'смотрю в базу, есть ли id пользователя к этому номеру')
            _fnd_user_id = read_base(int(_fnd_user_ph))
            if _fnd_user_id:
                print('В базе есть и телефон и id пользователя, ничего не записываю')
                return signer_id
            else:
                print('В базе нет телефона и id пользователя - записываю:', signer_id, _fnd_user_ph,
                      _get_username(signer_id))
                write_base(signer_id, int(_fnd_user_ph))
                return signer_id
        else:
            print(f"Номера телефона в посте {data.get('id')} НЕТ! Записывать нечего")
            return signer_id
    else:
        print(f"Пост {data.get('id')} без подписи")
        print(f"Ищу номер телефона в посте {data.get('id')}")
        _fnd_user_ph = find_user_func(data)
        if _fnd_user_ph:
            print(
                f"В посте {data.get('id')} есть такой телефон: {_fnd_user_ph} "
                f"смотрю в базу, есть ли id пользователя к этому номеру")
            _fnd_user_id = read_base(int(_fnd_user_ph))
            if _fnd_user_id:
                signer_id = _fnd_user_id
                print('signer_id присвоен из базы данных:', _get_username(signer_id))
                return signer_id
            else:
                print('В базе нет id для этого телефона, пост без подписи - ничего не записываю, отправитель Аноним')
                signer_id = 'Anonymously'
                return signer_id
        else:
            print(f"В посте {data.get('id')} нет ни номера телефона, ни подписи. отправитель Аноним")
            signer_id = 'Anonymously'
            return signer_id


def _get_username(user_id):
    session = vk_api.VkApi(token=config.tg_bot.vk_api_token)
    username = session.method('users.get', {'user_id': user_id})[0]
    return ' '.join((username['first_name'], username['last_name']))
