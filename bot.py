import telebot 
from config import *
from logic import *

# Создание экземпляра бота с использованием токена из конфигурационного файла.
bot = telebot.TeleBot(TOKEN)
manager = DB_Map(DATABASE)
manager.create_user_table()

# Обработчик команды '/start'
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

# Обработчик команды '/help'
@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, "Доступные команды: /show_city [город], /remember_city [город], /show_my_cities, /set_marker_color [цвет]")

# Обработчик команды '/set_marker_color'
@bot.message_handler(commands=['set_marker_color'])
def handle_set_marker_color(message):
    user_id = message.chat.id
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(user_id, "Укажи цвет: например, /set_marker_color blue или /set_marker_color #ff6600")
        return
    color = parts[1]
    manager.set_marker_color(user_id, color)
    bot.send_message(user_id, f"Цвет маркеров сохранён: {color}")

# Обработчик команды '/show_city'
@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    user_id = message.chat.id
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(user_id, "Укажи город: например, /show_city Paris")
        return
    city_name = ' '.join(parts[1:])  # объединяем все слова в название города
    marker_color = manager.get_marker_color(user_id)
    coordinates = manager.get_coordinates(city_name)
    if not coordinates:
        bot.send_message(user_id, f"Не могу найти город {city_name}. Убедись, что написан на английском и точно совпадает с БД.")
        return
    manager.create_graph(f'{user_id}.png', [city_name], marker_color=marker_color)
    with open(f'{user_id}.png', 'rb') as map:
        bot.send_photo(user_id, map)

# Обработчик команды '/remember_city'
@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    user_id = message.chat.id
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(user_id, "Укажи город: например, /remember_city Paris")
        return
    city_name = ' '.join(parts[1:])
    if manager.add_city(user_id, city_name):
        bot.send_message(user_id, f'Город {city_name} успешно сохранен!')
    else:
        bot.send_message(user_id, 'Такого города я не знаю. Убедись, что он написан на английском!')

# Обработчик команды '/show_my_cities'
@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    cities = manager.select_cities(message.chat.id)
    marker_color = manager.get_marker_color(message.chat.id)
    if cities:
        manager.create_graph(f'{message.chat.id}_cities.png', cities, marker_color=marker_color)
        with open(f'{message.chat.id}_cities.png', 'rb') as map:
            bot.send_photo(message.chat.id, map)
    else:
        bot.send_message(message.chat.id, "У вас пока нет сохраненных городов.")

# Запуск бота
if __name__=="__main__":
    bot.polling()
