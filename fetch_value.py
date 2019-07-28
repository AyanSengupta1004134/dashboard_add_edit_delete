import sqlite3

conn = sqlite3.connect('db/users.db')
cursor = conn.cursor()
sql = "Select * from users"
a = cursor.execute(sql)
rows = cursor.fetchall()
conn.commit()
print(rows)
print(len(rows))