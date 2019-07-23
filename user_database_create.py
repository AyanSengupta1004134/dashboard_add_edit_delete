import sqlite3

connection = sqlite3.connect('db/users.db')
cursor = connection.cursor()

sql = """Create table users (id INTEGER PRIMARY KEY AUTOINCREMENT, name varchar(100),
email varchar(100), username varchar(30), password varchar(100), register_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)"""
cursor.execute(sql)
connection.commit()