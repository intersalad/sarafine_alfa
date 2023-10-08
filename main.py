import datetime

import telebot
from telebot import types
import pandas as pd
import json
import requests

bot = telebot.TeleBot('6502285968:AAEFgcbUoxHYT8H7z-X-G2g72TellFRwQMo')


def help():
    print("Добавить новую категорию - /new_cat")
    print("Добавить нового специалиста - /new_spec")
    print("Добавить нового пользователя - /new_user")
    print("Добавить новую рекомендацию - /new_rec")
    print("Вывести список пользователей - /user_list")
    print("Вывести список категорий - /cat_list")
    print("Вывести список специалистов - /spec_list")


def count_elements(my_dict):
    c = 0
    for v in my_dict.values():
        if isinstance(v, dict):
            c += count_elements(v)
        elif isinstance(v, list):
            c += len(v)
        elif isinstance(v, str):
            c += 1
    return c


def input_to_number(inp):
    inp = str(inp).replace(' ', '')
    num = ''
    for i in str(inp):
        if i in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            num += i
    print('num -> ', num)
    return num


def get_friends_list(user_id):
    access_token = '1f14b34d1f14b34d1f14b34d151c0751b111f141f14b34d7b4e42f7fbf098222890c6b7'  # Здесь нужно заменить на свой access token VK API
    api_version = '5.154'
    url = f'https://api.vk.com/method/friends.get?user_id={user_id}&access_token={access_token}&v={api_version}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        friends_data = response.json()['response']  # Получаем данные о списке друзей
        friends_list = friends_data['items']  # Получаем список id друзей пользователя
        return friends_list
    except requests.exceptions.HTTPError as error:
        print(f'HTTP error occurred: {error}')
    except requests.exceptions.RequestException as error:
        print(f'Request exception occurred: {error}')
    except KeyError:
        print('Error: Unable to retrieve friends list.')


def get_vk_name(user_id):
    access_token = '1f14b34d1f14b34d1f14b34d151c0751b111f141f14b34d7b4e42f7fbf098222890c6b7'
    api_version = '5.154'
    url = f'https://api.vk.com/method/users.get?user_ids={user_id}&access_token={access_token}&lang=ru&name_case=gen&v={api_version}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        user_data = response.json()['response']
        vk_name = user_data[0]['first_name']
        vk_surname = user_data[0]['last_name']
        name = str(vk_name) + ' ' + str(vk_surname)
        return name
    except requests.exceptions.HTTPError as error:
        print(f'HTTP error occurred: {error}')
    except requests.exceptions.RequestException as error:
        print(f'Request exception occurred: {error}')
    except KeyError:
        print('Error: Unable to retrieve friends list.')


def search(poisk, user_id):
    if '  —  ' not in poisk.text:
        poisk.text = poisk.text.title()
        with open("users_list.json", "r") as my_file:
            users_list_json = my_file.read()
        users_list = json.loads(users_list_json)

        with open("rec_list.json", "r") as my_file:
            rec_list_json = my_file.read()
        rec_list = json.loads(rec_list_json)

        with open("spec_list.json", "r") as my_file:
            specs_list_json = my_file.read()
        specs_list = json.loads(specs_list_json)

        if poisk.text in specs_list:
            bot.send_message(user_id, 'Список найденных специалистов:')
            print('Да', poisk.text, 'у нас имеются')
            u_id = users_list[str(user_id)][2]
            friends_list = get_friends_list(u_id)
            print(f'Список id друзей пользователя {u_id}: {friends_list}')
            for i in friends_list:
                if str(i) in str(rec_list):
                    print('нашлась рекомендация от https://vk.com/id', i, sep='')
                    for j in rec_list[str(i)]:
                        #print(j)
                        if str(j) in str(specs_list[str(poisk.text)]):
                            for k in specs_list[str(poisk.text)]:
                                if k[0] == j:
                                    print('опана! нашли теbе спеца. Его sarafine_id', k)
                                    out = str(k[1]) + ' +' + str(k[2]) + '\n\n' + 'Рекомендация от ' + get_vk_name(i) + \
                                          '\n' + 'https://vk.com/id' + str(i) + '\n\n'
                                    bot.send_message(user_id, out)

        else:
            bot.send_message(user_id, 'Сорян, таких спецов у нас нет')
            print('Сорян, таких спецов у нас нет')


@bot.message_handler(commands=['new_spec'])
def new_spec(message):
    with open("spec_list.json", "r") as my_file:
        specs_list_json = my_file.read()
    specs_list = json.loads(specs_list_json)

    user_id = message.from_user.id
    markup = types.ReplyKeyboardMarkup(row_width=1)
    for i in specs_list:
        out = i
        markup.add(types.KeyboardButton(out))
    markup.add(types.KeyboardButton('Выйти'))
    msg = bot.send_message(user_id, 'Выберите категорию:', reply_markup=markup)
    bot.register_next_step_handler(msg, new_spec_2)


def new_spec_2(message):
    n_cat = message.text
    user_id = message.from_user.id
    print('message -> ', n_cat)
    if n_cat == 'Выйти':
        print('ок выхожу')
        markup = types.ReplyKeyboardRemove()
        bot.send_message(user_id, 'Главное меню', reply_markup=markup)
    else:
        markup = types.ReplyKeyboardRemove()
        bot.send_message(user_id, 'Выбрана категория ' + n_cat, reply_markup=markup)
        msg = bot.send_message(user_id, 'Введите имя и фамилию специалиста:')
        bot.register_next_step_handler(msg, new_spec_3, category=n_cat)


def new_spec_3(message, category):
    name = str(message.text).split()
    user_id = message.from_user.id

    if len(name) == 2:
        msg = bot.send_message(user_id, 'Введите телефонный номер специалиста:')
        bot.register_next_step_handler(msg, new_spec_4, category=category, name=name)
    else:
        bot.send_message(message.from_user.id, 'Повторите попытку:')
        new_spec(message)


def new_spec_4(message, category, name):
    with open("spec_list.json", "r") as my_file:
        specs_list_json = my_file.read()
    specs_list = json.loads(specs_list_json)
    user_id = message.from_user.id

    num = input_to_number(message.text)
    if num != '':
        n_id = count_elements(specs_list)
        print('выдан айди', n_id)
        temp_d = specs_list[category]
        temp_d.append([n_id, name, num])
        specs_list[category] = temp_d
        name_out = str(name[0]) + ' ' + str(name[1])
        out = 'Добавлен специалист!' + '\n\n' + 'Категория: ' + str(category) + '\n' + 'Имя: ' + name_out + '\n' + \
              'Телефон: +' + str(num) + '\n' + 'ID: ' + str(n_id)
        bot.send_message(user_id, out)
        bot.send_message(user_id, 'Все ок')
    else:
        bot.send_message(message.from_user.id, 'Повторите попытку:')
        new_spec(message)

    specs_list_json = json.dumps(specs_list)
    with open("spec_list.json", "w") as my_file:
        my_file.write(specs_list_json)


@bot.message_handler(commands=['new_rec'])
def new_rec(message):
    bot.send_message(message.from_user.id, 'Введите номер мастера: ')
    bot.register_next_step_handler(message, new_rec_2)


def new_rec_2(message):
    with open("spec_list.json", "r") as my_file:
        specs_list_json = my_file.read()
    specs_list = json.loads(specs_list_json)

    num = input_to_number(message.text)
    not_find = True
    for i in specs_list:
        if not_find:
            for j in specs_list[i]:
                if not_find and j[2] == str(num):
                    spec_name = j[1]
                    spec_id = j[0]
                    msg = bot.send_message(message.from_user.id, 'Введите Фамилию специалиста')
                    bot.register_next_step_handler(msg, new_rec_3, spec_name=spec_name, spec_id=spec_id)
                    not_find = False
    if not_find:
        bot.send_message(message.from_user.id, 'Не нашли такого специалиста на платформе. ' + '\n' +
                                               'Чтобы его добавить воспользуйтесь командой /new_spec')


def new_rec_3(message, spec_name, spec_id):
    with open("rec_list.json", "r") as my_file:
        rec_list_json = my_file.read()
    rec_list = json.loads(rec_list_json)

    user_id = str(message.from_user.id)
    out = ''

    if str(message.text) in spec_name:
        if str(user_id) not in rec_list:
            rec_list[user_id] = [spec_id]
        else:
            if spec_id not in list(rec_list[user_id]):
                temp_d = list(rec_list[user_id])
                temp_d.append(spec_id)
                rec_list[user_id] = temp_d
                out = 'Рекомендация успешно добавлена!'
                print('')
            else:
                out = 'Вы уже рекомендовали этого специалиста'

        rec_list_json = json.dumps(rec_list)
        with open("rec_list.json", "w") as my_file:
            my_file.write(rec_list_json)
    else:
        out = 'Специалист с такими данными не найдем. Возможно Вы ошиблись. Попробуйте еще раз /new_rec'
    bot.send_message(message.from_user.id, out)


def new_user(id, name, surname, username, v_link):
    with open("users_list.json", "r") as my_file:
        users_list_json = my_file.read()
    users_list = json.loads(users_list_json)

    if str(v_link)[:4] == 'http':
        print(str(v_link[:4]))
        v_link = str(v_link)[15:]
        print(v_link)

    access_token = '1f14b34d1f14b34d1f14b34d151c0751b111f141f14b34d7b4e42f7fbf098222890c6b7'
    api_version = '5.154'
    url = f'https://api.vk.com/method/users.get?user_ids={v_link}&access_token={access_token}&v={api_version}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        user_data = response.json()['response']
        print(user_data)
        true_id = user_data[0]['id']
        vk_name = user_data[0]['first_name']
        vk_surname = user_data[0]['last_name']
        print(true_id)
    except requests.exceptions.HTTPError as error:
        print(f'HTTP error occurred: {error}')
        bot.send_message(id, 'Попробуйте еще раз')
    except requests.exceptions.RequestException as error:
        print(f'Request exception occurred: {error}')
        bot.send_message(id, 'Попробуйте еще раз')
    except KeyError:
        print('Error: Unable to retrieve friends list.')
        bot.send_message(id, 'Попробуйте еще раз')

    if str(id) not in users_list:
        users_list[id] = [vk_name, vk_surname, true_id, name, surname, username]
        bot.send_message(id, str('Добро пожаловать! Вы ' + str(len(users_list)) + ' пользователь'))
    else:
        bot.send_message(id, 'Рады видеть вас снова')
    users_list_json = json.dumps(users_list)
    with open("users_list.json", "w") as my_file:
        my_file.write(users_list_json)


rec_list = {'id1': [1, 2, 3], 'id2': [1, 237, 4]}

print("Sarafine v.1.0")


@bot.message_handler(commands=['cat_list'])
def cat_list(message):
    with open("spec_list.json", "r") as my_file:
        specs_list_json = my_file.read()
    specs_list = json.loads(specs_list_json)
    markup = types.ReplyKeyboardMarkup(row_width=1)
    out = ''
    for i in specs_list:
        out = i + '  —  ' + str(len(specs_list[i])) + "\n"
        markup.add(types.KeyboardButton(out))
    msg = bot.send_message(message.from_user.id, 'Категории на платформе:', reply_markup=markup)
    bot.register_next_step_handler(msg, spec_list)


def spec_list(message):
    with open("spec_list.json", "r") as my_file:
        specs_list_json = my_file.read()
    specs_list = json.loads(specs_list_json)
    category = str(message.text).split('  —  ')[0]
    for i in specs_list:
        if str(i) == category:
            out = 'Специалисты в категории ' + str(i) + '\n' + 'Количество: ' + str(len(specs_list[i])) + '\n\n'
            for j in specs_list[i]:
                out += str(j[1]) + ' +' + str(j[2]) + '\n'
            break
    de = types.ReplyKeyboardRemove()
    bot.send_message(message.from_user.id, out, reply_markup=de)
    print(datetime.datetime, ' -> ', message.from_user.id, 'запросил специалистов в категории', str(i))


@bot.message_handler(commands=['user_list'])
def show_users_list(message):
    with open("users_list.json", "r") as my_file:
        users_list_json = my_file.read()
    users_list = json.loads(users_list_json)

    out = ''
    for i in users_list:
        out += '@' + str(users_list[i][-1]) + '\n'
    bot.send_message(message.from_user.id, out)
    print(datetime.datetime, ' -> ', message.from_user.id, ' запросил список пользователей')


@bot.message_handler(commands=['new_cat'])
def new_cat(message):
    with open("spec_list.json", "r") as my_file:
        specs_list_json = my_file.read()
    specs_list = json.loads(specs_list_json)
    cat = str(input('Введите название новой категории:'))

    specs_list[cat.title()] = []

    out = 'Добавлена категория ' + cat.title()
    bot.send_message(message.from_user.id, out)

    specs_list_json = json.dumps(specs_list)
    with open("spec_list.json", "w") as my_file:
        my_file.write(specs_list_json)


@bot.message_handler(commands=['start'])
def url(message):
    with open("users_list.json", "r") as my_file:
        users_list_json = my_file.read()
    users_list = json.loads(users_list_json)
    bot.send_message(message.from_user.id, 'Платформа Sarafine v1.0')
    bot.send_message(message.from_user.id, 'https://t.me/sarafine_alfa_bot/inter')
    if str(message.from_user.id) not in users_list:
        bot.send_message(message.from_user.id, 'Для использования напишите ссылку на ваш профиль VK')
        bot.register_next_step_handler(message, vk_link)


def vk_link(message):
    ms = message.from_user
    new_user(ms.id, ms.first_name, ms.last_name, ms.username, message.text)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    search(message, message.from_user.id)


bot.polling()


