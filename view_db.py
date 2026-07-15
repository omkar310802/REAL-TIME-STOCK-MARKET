import sqlite3

conn = sqlite3.connect("stockintel.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", cursor.fetchall())

cursor.execute("SELECT * FROM User")
print(cursor.fetchall())

conn.close()