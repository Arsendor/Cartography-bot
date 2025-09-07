import sqlite3
from config import *  
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

class DB_Map():
    def __init__(self, database):
        self.database = database
    
    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            # Таблица для городов пользователя
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            # Таблица для хранения цветов
            conn.execute('''CREATE TABLE IF NOT EXISTS user_prefs (
                                user_id INTEGER PRIMARY KEY,
                                marker_color TEXT DEFAULT 'r'
                            )''')
            # Автообновление таблицы user_prefs: добавляем новые колонки, если их нет
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(user_prefs)")
            columns = [row[1] for row in cur.fetchall()]
            if 'land_color' not in columns:
                conn.execute("ALTER TABLE user_prefs ADD COLUMN land_color TEXT DEFAULT 'lightgreen'")
            if 'ocean_color' not in columns:
                conn.execute("ALTER TABLE user_prefs ADD COLUMN ocean_color TEXT DEFAULT 'lightblue'")
            conn.commit()

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1
            else:
                return 0

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))
            return [row[0] for row in cursor.fetchall()]

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT lat, lng FROM cities WHERE city = ?''', (city_name,))
            return cursor.fetchone()

    # Методы для работы с цветами
    def set_colors(self, user_id, marker_color=None, land_color=None, ocean_color=None):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''
                INSERT INTO user_prefs(user_id, marker_color, land_color, ocean_color)
                VALUES(?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                marker_color=COALESCE(excluded.marker_color, marker_color),
                land_color=COALESCE(excluded.land_color, land_color),
                ocean_color=COALESCE(excluded.ocean_color, ocean_color)
            ''', (user_id, marker_color, land_color, ocean_color))
            conn.commit()

    def get_colors(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('SELECT marker_color, land_color, ocean_color FROM user_prefs WHERE user_id=?', (user_id,))
            row = cur.fetchone()
            if row:
                return row[0], row[1], row[2]
            else:
                return 'r', 'lightgreen', 'lightblue'

    # Создание карты с городами и заливкой
    def create_graph(self, path, cities, marker_color='r', land_color='lightgreen', ocean_color='lightblue'):
        # Получаем координаты всех городов
        coords = [self.get_coordinates(city) for city in cities if self.get_coordinates(city)]
        if not coords:
            return  # нет городов, ничего не строим

        lats = [lat for lat, lng in coords]
        lngs = [lng for lat, lng in coords]

        plt.figure(figsize=(14, 10))  # увеличиваем размер карты
        ax = plt.axes(projection=ccrs.PlateCarree())

        # Заливка суши и океана, добавление объектов
        ax.add_feature(cfeature.LAND, facecolor=land_color)
        ax.add_feature(cfeature.OCEAN, facecolor=ocean_color)
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.LAKES, facecolor=ocean_color)
        ax.add_feature(cfeature.RIVERS, edgecolor="blue")

        # Определяем область карты с запасом
        min_lng, max_lng = min(lngs)-10, max(lngs)+10
        min_lat, max_lat = min(lats)-5, max(lats)+5
        ax.set_extent([min_lng, max_lng, min_lat, max_lat], crs=ccrs.PlateCarree())

        # Отображаем города
        for city, (lat, lng) in zip(cities, coords):
            plt.plot([lng], [lat], color=marker_color, marker='o', markersize=10,
                     transform=ccrs.Geodetic())
            plt.text(lng + 1, lat + 1, city, horizontalalignment='left', fontsize=10,
                     transform=ccrs.Geodetic())

        plt.savefig(path, bbox_inches='tight')
        plt.close()


if __name__=="__main__":
    m = DB_Map(DATABASE)
    m.create_user_table()
