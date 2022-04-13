import os
import face_recognition
from sqlite3 import connect

conn = connect('database/eVision.db')
curs = conn.cursor()

try :
    curs.execute("CREATE TABLE face_data (id text, data text)")
    conn.commit()
except :
    print('face_date table exist')

try :
    curs.execute("CREATE TABLE users (id text, name text)")
    conn.commit()
except :
    print('user table exist')

if os.path.exists('database/eVision.db'):
    path = 'images/'
    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]
    
    for imagePath in imagePaths:  
        try :  
            id = int(os.path.split(imagePath)[-1].split(".")[1])
            face_load_file = face_recognition.load_image_file(imagePath)
            face_encode = face_recognition.face_encodings(face_load_file)[0]
            curs.execute("INSERT INTO face_data VALUES(?, ?)", (id, face_encode))
            conn.commit()
        except :
            print('Image not face')

else :
    print('not exist data model [encodings.pickle]')