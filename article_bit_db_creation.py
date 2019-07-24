import sqlite3
connection = sqlite3.connect('db/articles_fav.db')
cursor = connection.cursor()

sql = """Create table articles_fav (id INTEGER PRIMARY KEY AUTOINCREMENT, title varchar(255),
author varchar(100), body varchar(100), fav bit NOT NULL DEFAULT(0), create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)"""
cursor.execute(sql)
connection.commit()