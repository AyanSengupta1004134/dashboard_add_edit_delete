import sqlite3

connection = sqlite3.connect('db/temp_admin.db')
cursor = connection.cursor()

sql = """Create table temp_admin (id INTEGER PRIMARY KEY AUTOINCREMENT, username varchar(30), password varchar(100))"""
cursor.execute(sql)
connection.commit()