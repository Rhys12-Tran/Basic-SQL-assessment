import sqlite3
conn = sqlite3.connect("Task_Manager_Database.db")
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(Task)")
columns = cursor.fetchall()
for col in columns:
    print(col)
conn.close()

