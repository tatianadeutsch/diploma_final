from config import offset, line
import vk_api
import requests
import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange
from database import *


class VKBot:
    def __init__(self):
        print('Ура! Бот наконец-то создан!')
        TOKEN_GROUP = ''
        TOKEN_APP = ''
        self.vk = vk_api.VkApi(token=TOKEN_GROUP)
        self.longpoll = VkLongPoll(self.vk)
        self.url = 'https://api.vk.com/method/'
        self.params = {
            'access_token': TOKEN_APP,
            'v': '5.131'
        }

    def write_msg(self, user_id, message):
        self.vk.method('messages.send', {'user_id': user_id,
                                         'message': message,
                                         'random_id': randrange(10 ** 7)})

    # Определить имя пользователя, написавшему боту
    def name(self, user_id):
        url_name = self.url + 'users.get'
        params = {'user_ids': user_id,
                  }
        response = requests.get(url_name, params={**self.params, **params}).json()

        try:
            for info in response['response']:
                for key, value in info.items():
                    first_name = info.get('first_name')
                    return first_name

        except KeyError:
            self.write_msg(user_id, 'Ошибка получения токена. Укажите токен в TOKEN_GROUP')

    # Запросить возраст визави пользователя: ОТ
    def get_age_low(self, user_id):
        url_age_low = self.url + 'users.get'
        params = {'user_ids': user_id,
                  'fields': 'bdate'}
        response = requests.get(url_age_low, params={**self.params, **params}).json()

        try:
            for info in response['response']:
                date = info.get('bdate')
                date_list = date.split('.')
                if len(date_list) == 3:
                    year = int(date_list[2])
                    year_now = int(datetime.date.today().year)
                    return year_now - year
                elif len(date_list) == 2 or date not in response['response']:
                    self.write_msg(user_id, 'Введите возраст для своего визави (от 18 лет): ')
                    for event in self.longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                            age = event.text
                            if age >= 18:
                                return age
                            else:
                                self.write_msg(user_id, 'Введено неверное значение.')
                                continue
        except KeyError:
            self.write_msg(user_id, 'Ошибка получения токена. Укажите токен в TOKEN_GROUP')

    # Запросить возраст визави пользователя: ДО
    def get_age_high(self, user_id):
        url_age_high = self.url + 'users.get'
        params = {'user_ids': user_id,
                  'fields': 'bdate'}
        response = requests.get(url_age_high, params={**self.params, **params}).json()

        try:
            for info in response['response']:
                date = info.get('bdate')
                date_list = date.split('.')
                if len(date_list) == 3:
                    year = int(date_list[2])
                    year_now = int(datetime.date.today().year)
                    return year_now - year
                elif len(date_list) == 2 or date not in response['response']:
                    self.write_msg(user_id, 'Введите возраст для своего визави (до 99 лет) ')
                    for event in self.longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                            age = event.text
                            if age >= 18 and age <= 99 or age >= self.get_age_low:
                                return age
                            else:
                                self.write_msg(user_id, 'Введено неверное значение.')
                                continue
        except KeyError:
            self.write_msg(user_id, 'Ошибка получения токена. Укажите токен в TOKEN_GROUP')

    # Запросить пол визави пользователя и сменить на противоположный
    def get_sex(self, user_id):
        url_get_sex = self.url + 'users.get'
        params = {'user_ids': user_id,
                  'fields': 'sex'}
        response = requests.get(url_get_sex, params={**self.params, **params}).json()

        try:
            for info in response['response']:
                if info.get('sex') == 2:
                    sex = 1
                    return sex
                elif info.get('sex') == 1:
                    sex = 2
                    return sex
        except KeyError:
            self.write_msg(user_id, 'Ошибка получения токена. Укажите токен в TOKEN_GROUP')

    # Адаптация названия города к ИД города
    def cities(self, user_id, city_name):
        url_cities = self.url + 'database.getCities'
        params = {'country_id': 1,
                  'q': f'{city_name}',
                  'need_all': 0,
                  'count': 1000,
                  'v': '5.131'}
        response = requests.get(url_cities, params={**self.params, **params}).json()

        try:
            for info in response['response']['items']:
                found_city_name = info.get('title')
                if found_city_name == city_name:
                    found_city_id = info.get('id')
                    return int(found_city_id)

        except KeyError:
            self.write_msg(user_id, 'Ошибка получения токена. Укажите токен в TOKEN_GROUP')

    # Запросить название города визави пользователя
    def find_city(self, user_id):
        url_city = self.url + 'users.get'
        params = {'fields': 'city',
                  'user_ids': user_id,
                  'country_id': 1,
                  'need_all': 0,
                  'count': 1000,
                  }
        response = requests.get(url_city, params={**self.params, **params}).json()

        try:
            for info in response['response']:
                if 'city' in info:
                    city = info.get('city')
                    id = str(city.get('id'))
                    return id
                elif 'city' not in info:
                    self.write_msg(user_id, 'Введите название города своего визави: ')
                    for event in self.longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                            city_name = event.text
                            id_city = self.cities(user_id, city_name)
                            if id_city != '' or id_city != None:
                                return str(id_city)
                            else:
                                self.write_msg(user_id, 'Введено неверное значение.')
                                break
        except KeyError:
            self.write_msg(user_id, 'Ошибка получения токена. Укажите токен в TOKEN_GROUP')

    # Поиск визави по запрошенным данным + определние семейного/не семейного положения
    def find_user(self, user_id):
        url_search = self.url + 'users.search'
        params = {'v': '5.131',
                  'age_from': self.get_age_low(user_id),
                  'age_to': self.get_age_high(user_id),
                  'sex': self.get_sex(user_id),
                  'city': self.find_city(user_id),
                  'fields': 'is_closed, id, first_name, last_name',
                  'status': 1 or 6,
                  'count': 500}
        response = requests.get(url_search, params={**self.params, **params}).json()
        try:
            for person_dict in response['response']['items']:
                if person_dict.get('is_closed') == False:
                    first_name = person_dict.get('first_name')
                    last_name = person_dict.get('last_name')
                    vk_id = str(person_dict.get('id'))
                    vk_link = 'vk.com/id' + str(person_dict.get('id'))
                    insert_data_users(first_name, last_name, vk_id, vk_link)
                else:
                    continue
            return f'Поиск завершён'
        except (KeyError, LookupError, SyntaxError, TypeError):
            self.write_msg(user_id, "Произошла ошибка обработки данных .json. Попробуйте изменить критерии поиска")

    # Получить фотографии
    def get_photos_id(self, user_id):
        url_photos_id = self.url + 'photos.get'
        params = {
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 'likes',
            'photo_sizes': '1',
            'count': 25
        }
        response = requests.get(url_photos_id, params={**self.params, **params}).json()

        photos = dict()
        for info_user in response['response']['items']:
            photo_id = str(info_user.get('id'))
            i_likes = info_user.get('likes')
            if i_likes.get('count'):
                likes = i_likes.get('count')
                photos[likes] = photo_id
        list_of_ids = sorted(photos.items(), reverse=True)
        return list_of_ids

    # Фото номер 1
    def get_photo_1(self, user_id):
        list = self.get_photos_id(user_id)
        count = 0
        for photo_user in list:
            count += 1
            if count == 1:
                return photo_user[1]

    # Фото номер 2
    def get_photo_2(self, user_id):
        list = self.get_photos_id(user_id)
        count = 0
        for photo_user in list:
            count += 1
            if count == 2:
                return photo_user[1]

    # Фото номер 3
    def get_photo_3(self, user_id):
        list = self.get_photos_id(user_id)
        count = 0
        for photo_user in list:
            count += 1
            if count == 3:
                return photo_user[1]

    # Отправить 1 фотографию
    def send_photo_1(self, user_id, message, offset):
        self.vk.method('messages.send', {'user_id': user_id,
                                         'message': message,
                                         'attachment': f'photo{self.person_id(offset)}_{self.get_photo_1(self.person_id(offset))}',
                                         'random_id': 0})

    # Отправить 2 фотографию
    def send_photo_2(self, user_id, message, offset):
        self.vk.method('messages.send', {'user_id': user_id,
                                         'message': message,
                                         'attachment': f'photo{self.person_id(offset)}_{self.get_photo_2(self.person_id(offset))}',
                                         'random_id': 0})

    # Отправить 3 фотографию
    def send_photo_3(self, user_id, message, offset):
        self.vk.method('messages.send', {'user_id': user_id,
                                         'message': message,
                                         'attachment': f'photo{self.person_id(offset)}_{self.get_photo_3(self.person_id(offset))}',
                                         'random_id': 0})

    def find_persons(self, user_id, offset):
        self.write_msg(user_id, self.found_person_info(offset))
        self.person_id(offset)
        insert_data_seen_users(self.person_id(offset), offset)  # offset
        self.get_photos_id(self.person_id(offset))
        self.send_photo_1(user_id, 'Фото номер 1', offset)
        if self.get_photo_2(self.person_id(offset)) != None:
            self.send_photo_2(user_id, 'Фото номер 2', offset)
            self.send_photo_3(user_id, 'Фото номер 3', offset)
        else:
            self.write_msg(user_id, f'Больше фотографий нет')

    # Инфа о визави
    def found_person_info(self, offset):
        info_person = select(offset)
        list_person = []
        for user in info_person:
            list_person.append(user)
        return f'{list_person[0]} {list_person[1]}, ссылка - {list_person[3]}'

    # ИД визави
    def person_id(self, offset):
        info_person = select(offset)
        list_person = []
        for id in info_person:
            list_person.append(id)
        return str(list_person[2])


bot = VKBot()
