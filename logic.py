import sqlite3
from config import *  
import matplotlib
matplotlib.use('Agg')  # Для работы без GUI
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

class DB_Map():
    def __init__(self, database):
        self.database = database
    
    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS user_prefs (
                                user_id INTEGER PRIMARY KEY,
                                marker_color TEXT DEFAULT 'r'
                            )''')
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

    def set_marker_color(self, user_id, color):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('INSERT INTO user_prefs(user_id, marker_color) VALUES(?, ?) \
                          ON CONFLICT(user_id) DO UPDATE SET marker_color=excluded.marker_color',
                         (user_id, color))
            conn.commit()

    def get_marker_color(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('SELECT marker_color FROM user_prefs WHERE user_id=?', (user_id,))
            row = cur.fetchone()
            return row[0] if row else 'r'

    def create_graph(self, path, cities, marker_color='r'):
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.stock_img()
        for city in cities:
            coordinates = self.get_coordinates(city)
            if coordinates:
                lat, lng = coordinates
                plt.plot([lng], [lat], color=marker_color, marker='o', markersize=5,
                         transform=ccrs.Geodetic())
                plt.text(lng + 3, lat + 12, city, horizontalalignment='left', transform=ccrs.Geodetic())
        plt.savefig(path)
        plt.close()

if __name__=="__main__":
    m = DB_Map(DATABASE)
    m.create_user_table()
