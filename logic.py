import sqlite3
from config import *  
import matplotlib
matplotlib.use('Agg')  # Установка бэкенда Matplotlib для сохранения файлов в памяти без отображения окна
import matplotlib.pyplot as plt
import cartopy.crs as ccrs  # Импорт модуля для работы с картографическими проекциями

class DB_Map():
    def __init__(self, database):
        self.database = database  # Инициализация пути к базе данных
    
    def create_user_table(self):
        conn = sqlite3.connect(self.database)  # Подключение к базе данных
        with conn:
            # Создание таблицы, если она не существует, для хранения городов пользователей
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()  # Подтверждение изменений

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Запрос к базе данных на наличие города по имени
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]
                # Добавление города в список городов пользователя
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1  # Возврат успеха операции
            else:
                return 0  # Город не найден

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Выбор всех городов пользователя
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))
            cities = [row[0] for row in cursor.fetchall()]
            return cities  # Возврат списка городов пользователя

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            # Получение координат города по его имени
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates  # Возврат координат города

    def create_graph(self, path, cities):
      # Создание нового графического контекста с указанием проекции карты PlateCarree.
      # PlateCarree - это простая географическая проекция, где долготы и широты отображаются
      # как вертикальные и горизонтальные линии соответственно.
      ax = plt.axes(projection=ccrs.PlateCarree())
      
      # Добавление на карту стандартного изображения земного шара.
      # Это фоновое изображение предоставляется библиотекой Cartopy и включает в себя 
      # визуализацию поверхности земли, океанов и основных рельефов.
      ax.stock_img()
      
      # Итерация по списку городов для отображения на карте.
      for city in cities:
          # Получение координат города. Эта функция должна возвращать кортеж с широтой и долготой города.
          coordinates = self.get_coordinates(city)
          
          # Проверка, что координаты города успешно получены.
          if coordinates:
              # Распаковка кортежа координат в переменные lat (широта) и lng (долгота).
              lat, lng = coordinates
              
              # Отрисовка маркера на карте в позиции, заданной координатами города.
              # 'color='r'' задает цвет маркера красный, 'linewidth=1' задает толщину линии маркера,
              # 'marker='.'' указывает на форму маркера (точка).
              plt.plot([lng], [lat], color='r', linewidth=1, marker='.', transform=ccrs.Geodetic())
              
              # Добавление текста (названия города) рядом с маркером.
              # '+3' и '+12' к долготе и широте задают смещение текста относительно маркера,
              # чтобы текст не перекрывал маркер и был читаемым.
              plt.text(lng + 3, lat + 12, city, horizontalalignment='left', transform=ccrs.Geodetic())
    
      # Сохранение созданного изображения в файл по пути, указанному в аргументе 'path'.
      plt.savefig(path)
      
      # Закрытие контекста matplotlib для освобождения ресурсов.
      plt.close()

    def draw_distance(self, city1, city2):
        # Рисование линии между двумя городами для отображения расстояния
        city1_coords = self.get_coordinates(city1)
        city2_coords = self.get_coordinates(city2)
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
        ax.stock_img()
        plt.plot([city1_coords[1], city2_coords[1]], [city1_coords[0], city2_coords[0]], color='red', linewidth=2, marker='o', transform=ccrs.Geodetic())
        plt.text(city1_coords[1] + 3, city1_coords[0] + 12, city1, horizontalalignment='left', transform=ccrs.Geodetic())
        plt.text(city2_coords[1] + 3, city2_coords[0] + 12, city2, horizontalalignment='left', transform=ccrs.Geodetic())
        plt.savefig('distance_map.png')
        plt.close()

if __name__=="__main__":
    m = DB_Map(DATABASE)  # Создание объекта для работы с базой данных
    m.create_user_table()  # Создание таблицы пользователей и городов, если она еще не существует