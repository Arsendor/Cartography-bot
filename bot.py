import telebot 
from config import *
from logic import *

# Создание экземпляра бота
bot = telebot.TeleBot(TOKEN)
manager = DB_Map(DATABASE)
manager.create_user_table()

# Команда /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

# Команда /help
@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, "Доступные команды: /show_city [город], /remember_city [город], /show_my_cities, /set_marker_color [цвет], /set_colors [маркер] [суша] [океан]")

# Команда /set_marker_color (только маркер, остальные цвета сохраняются)
@bot.message_handler(commands=['set_marker_color'])
def handle_set_marker_color(message):
    user_id = message.chat.id
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(user_id, "Укажи цвет маркера: например, /set_marker_color red или /set_marker_color #ff6600")
        return
    color = parts[1]
    marker, land, ocean = manager.get_colors(user_id)
    manager.set_colors(user_id, marker_color=color, land_color=land, ocean_color=ocean)
    bot.send_message(user_id, f"Цвет маркера сохранён: {color}")

# Команда /set_colors (маркер, суша, океан)
@bot.message_handler(commands=['set_colors'])
def handle_set_colors(message):
    user_id = message.chat.id
    parts = message.text.split()
    if len(parts) != 4:
        bot.send_message(user_id, "Укажи три цвета: /set_colors [маркер] [суша] [океан], например: /set_colors red lightgreen lightblue")
        return
    marker, land, ocean = parts[1], parts[2], parts[3]
    manager.set_colors(user_id, marker_color=marker, land_color=land, ocean_color=ocean)
    bot.send_message(user_id, f"Цвета обновлены:\nМаркер: {marker}\nСуша: {land}\nОкеан: {ocean}")

# Команда /show_city
@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    user_id = message.chat.id
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(user_id, "Укажи город: например, /show_city Paris")
        return
    city_name = ' '.join(parts[1:])
    marker_color, land_color, ocean_color = manager.get_colors(user_id)
    coordinates = manager.get_coordinates(city_name)
    if not coordinates:
        bot.send_message(user_id, f"Не могу найти город {city_name}. Убедись, что написан на английском и совпадает с БД.")
        return
    manager.create_graph(f'{user_id}.png', [city_name],
                         marker_color=marker_color,
                         land_color=land_color,
                         ocean_color=ocean_color)
    with open(f'{user_id}.png', 'rb') as map:
        bot.send_photo(user_id, map)

# Команда /remember_city
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

# Команда /show_my_cities
@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    cities = manager.select_cities(message.chat.id)
    marker_color, land_color, ocean_color = manager.get_colors(message.chat.id)
    if cities:
        manager.create_graph(f'{message.chat.id}_cities.png', cities,
                             marker_color=marker_color,
                             land_color=land_color,
                             ocean_color=ocean_color)
        with open(f'{message.chat.id}_cities.png', 'rb') as map:
            bot.send_photo(message.chat.id, map)
    else:
        bot.send_message(message.chat.id, "У вас пока нет сохраненных городов.")

# Запуск бота
if __name__=="__main__":
    bot.polling()
