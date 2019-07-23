import sqlite3
connection = sqlite3.connect('db/articles.db')
cursor = connection.cursor()

sql = """Create table articles (id INTEGER PRIMARY KEY AUTOINCREMENT, title varchar(255),
author varchar(100), body varchar(100), create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)"""
cursor.execute(sql)
connection.commit()