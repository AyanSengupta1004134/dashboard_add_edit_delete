import sqlite3

connection = sqlite3.connect('db/admin.db')
cursor = connection.cursor()

sql = """Create table admin (id INTEGER PRIMARY KEY AUTOINCREMENT, username varchar(30), password varchar(100))"""
cursor.execute(sql)
connection.commit()