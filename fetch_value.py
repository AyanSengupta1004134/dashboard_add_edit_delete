import sqlite3

conn = sqlite3.connect('db/articles_fav.db')
cursor = conn.cursor()
sql = "Select * from articles_fav "
a = cursor.execute(sql)
rows = cursor.fetchall()
conn.commit()
print(rows)
print(len(rows))