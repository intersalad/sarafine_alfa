import telebot
import requests

# Устанавливаем токен для телеграм бота
bot_token = '6502285968:AAEFgcbUoxHYT8H7z-X-G2g72TellFRwQMo'
bot = telebot.TeleBot(bot_token)

# Устанавливаем токен и настройки для API VK
vk_token = '30yTr5w9ufa57LYfghej'
vk_api_version = '5.131'


# Функция для авторизации пользователя через ВКонтакте
def vk_auth(chat_id):
    # Формируем ссылку для авторизации
    auth_url = f'https://oauth.vk.com/authorize?client_id=51634940&redirect_uri=https://oauth.vk.com/blank.html&scope=offline&display=page&response_type=token&v={vk_api_version}'
    # Отправляем сообщение с ссылкой на авторизацию
    bot.send_message(chat_id, f'Авторизуйтесь через ВКонтакте: {auth_url}')


# Обрабатываем команду /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    vk_auth(chat_id)  # Вызываем функцию авторизации


# Обрабатываем ответ от ВКонтакте
@bot.message_handler(func=lambda message: True)
def handle_auth_response(message):
    # Получаем параметры из URL
    response_params = message.text.split('#')[1].split('&')
    access_token = response_params[0].split('=')[1]
    user_id = response_params[2].split('=')[1]

    # Запрос данных пользователя ВКонтакте
    vk_api_url = f'https://api.vk.com/method/users.get?user_ids={user_id}&fields=bdate,city,country&access_token={access_token}&v={vk_api_version}'
    response = requests.get(vk_api_url).json()

    # Обрабатываем данные пользователя
    if 'response' in response:
        user_info = response['response'][0]
        bot.send_message(message.chat.id, f'Добро пожаловать, {user_info["first_name"]} {user_info["last_name"]}!')

# Запускаем бота
bot.polling()
