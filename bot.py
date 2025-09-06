import telebot
from config import *
from logic import *

# Создание экземпляра бота с использованием токена из конфигурационного файла.
bot = telebot.TeleBot(TOKEN)

# Обработчик команды '/start', отправляет приветственное сообщение и предлагает помощь.
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

# Обработчик команды '/help', отправляет список доступных команд.
@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, "Доступные команды: /show_city [город], /remember_city [город], /show_my_cities")

# Обработчик команды '/show_city', отображает карту с указанным городом.
@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    city_name = message.text.split()[-1]
    user_id = message.chat.id
    manager.create_graph(f'{user_id}.png', [city_name])  # Создание карты для города
    with open(f'{user_id}.png', 'rb') as map:  # Открытие и отправка карты пользователю
        bot.send_photo(user_id, map)

# Обработчик команды '/remember_city', сохраняет указанный город в базу данных.
@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    user_id = message.chat.id
    city_name = message.text.split()[-1]
    if manager.add_city(user_id, city_name):  # Проверка и добавление города в БД
        bot.send_message(message.chat.id, f'Город {city_name} успешно сохранен!')
    else:
        bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')

# Обработчик команды '/show_my_cities', отображает карту со всеми сохраненными городами пользователя.
@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    cities = manager.select_cities(message.chat.id)  # Получение списка городов пользователя
    if cities:
        manager.create_graph(f'{message.chat.id}_cities.png', cities)  # Создание карты для всех городов
        with open(f'{message.chat.id}_cities.png', 'rb') as map:  # Открытие и отправка карты
            bot.send_photo(message.chat.id, map)
    else:
        bot.send_message(message.chat.id, "У вас пока нет сохраненных городов.")

# Запуск бота
if __name__=="__main__":
    manager = DB_Map(DATABASE)  # Инициализация менеджера базы данных
    bot.polling()