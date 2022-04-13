from sqlite3 import connect

conn = connect('database/eVision.db')
curs = conn.cursor()

curs.execute("SELECT id, data FROM face_data")
for id, data in curs.fetchall():
    print(id, data)

conn.close()
