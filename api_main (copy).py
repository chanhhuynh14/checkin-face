from sqlite3 import connect
import cv2
import face_recognition
import tornado.ioloop
import tornado.web
import os
import time
import json
import numpy
import pickle
import os.path

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir,'database/eVision.db' )
class home(tornado.web.RequestHandler):
    def get(self):
        self.write("Welcome to eVision")
class training(tornado.web.RequestHandler):
    def post(self):
        try:
            imgIn = self.request.files["image"][0]
            id =  self.get_argument('iduser')
            name =  self.get_argument('name')
            list_id_face= []
            imgInLink = open(f"img/{imgIn.filename}", "wb")
            imgInLink.write(imgIn.body)
            imgInLink.close()
            image_input = face_recognition.load_image_file(f'img/{imgIn.filename}')
            #if os.path.exists(f"img/{imgIn.filename}"):
            #    os.remove(f"img/{imgIn.filename}")
            small_image= cv2.resize(image_input,(0,0),fx= .25,fy= .25)
            face_locations = face_recognition.face_locations(small_image)    
            face_encoded = face_recognition.face_encodings(small_image,face_locations)
            try:
               ## Pickle the list into a string
               face_pickled_data = pickle.dumps(face_encoded[0]) 
            except IndexError:
            	self.write("Not found")
            else:
                conn = connect('database/eVision.db')
                cur = conn.cursor()
                cur.execute("SELECT data FROM face_data WHERE id=?", (id,))
                
                rows = cur.fetchall()
               
                if len(rows)==0:
                    conn_1 = connect('database/eVision.db')
                    curs_1 = conn_1.cursor()
                    curs_1.execute("INSERT INTO face_data VALUES(?, ?)", (id, face_pickled_data))
                    curs_1.execute("INSERT INTO users VALUES(?, ?)", (id, name))
                    conn_1.commit()
                    conn_1.close()
                else:
                	for each in rows:
                		for face_stored_pickled_data in each:
                			face_data = pickle.loads(face_stored_pickled_data)
                			results = face_recognition.compare_faces([face_data], face_encoded[0],0.35)
                	if True in results:
                				self.write("Update")
                				conn_2 = connect('database/eVision.db')
                				curs_2 = conn_2.cursor()
                				curs_2.execute("INSERT INTO face_data VALUES(?, ?)", (id, face_pickled_data))
                				conn_2.commit()
                				conn_2.close()
                				return
                	else: 
                				self.write("fail") 
                    
                conn.close()
    
                
        except Exception as e :
             self.write(e)

class deleteid(tornado.web.RequestHandler):
	def post(self):
		try:
			id =  self.get_argument('iduser')
			conn = connect('database/eVision.db')
			cur = conn.cursor()
			cur.execute("DELETE FROM face_data WHERE id=?", (id,))
			cur.execute("DELETE FROM users WHERE id=?", (id,))
			conn.commit()
			if cur.rowcount ==0:
				self.write("Not found ID")
			else:
			    self.write("Delete success") 

		except Exception as e:
			print(e)

class whoisthat(tornado.web.RequestHandler) :
    def post(self):
        list_id_face= []
        list_data_face= []
        list_username = []
        conn = connect(db_path)
        curs = conn.cursor()
        curs.execute("SELECT id FROM face_data")
        for id in curs.fetchall():
            list_id_face.append(id)
            
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM face_data")
        rows = cursor.fetchall()
        conn = connect(db_path)
        curs = conn.cursor()
        curs.execute("SELECT id, name FROM users")
        for id, name in curs.fetchall():
            list_username.append({"id" : id, "name" : name})
        try :
            imgIn = self.request.files["image"][0]
            imgInLink = open(f"img/{imgIn.filename}", "wb")
            imgInLink.write(imgIn.body)
            imgInLink.close()
            image_input = face_recognition.load_image_file(f'img/{imgIn.filename}')
            ##if os.path.exists(f"img/{imgIn.filename}"):
            ##    os.remove(f"img/{imgIn.filename}")
            face_locations = face_recognition.face_locations(image_input)
            face_encoded = face_recognition.face_encodings(image_input,face_locations)[0]
            for each in rows:
                for face_stored_pickled_data in each:
                	face_data = pickle.loads(face_stored_pickled_data)
                	results = face_recognition.compare_faces([face_data], face_encoded[0],0.6)
                	print(results)
                            
            name_main = "Unknown" 
            if True in results:
                    print('do')
                    first_match_index = matches.index(True)
                    for person in list_username:
                        if(person["id"] == list_id_face[first_match_index]):
                            name_main = person["name"]

            self.write(name_main);
            conn.close()
        except:	
            self.write("This image can not detect face")


class comparetwoface(tornado.web.RequestHandler) :
    def post(self):
        try:
            start = time.time()
            image_1 = self.request.files["image_1"][0]
            path_image_1 = f"img/{image_1.filename}"
            imgInLink_1 = open(path_image_1, "wb")
            imgInLink_1.write(image_1.body)
            imgInLink_1.close()
            image_input_1 = face_recognition.load_image_file(path_image_1)
            if os.path.exists(path_image_1):
                os.remove(path_image_1)
            #small_image_1= cv2.resize(image_input_1,(0,0),fx= .30,fy= .30)
            
            image_2 = self.request.files["image_2"][0]
            path_image_2 = f"img/{image_2.filename}"
            imgInLink_2 = open(path_image_2, "wb")
            imgInLink_2.write(image_2.body)
            imgInLink_2.close()
            image_input_2 = face_recognition.load_image_file(path_image_2)
            if os.path.exists(path_image_2):
                os.remove(path_image_2)
            #small_image_2 = cv2.resize(image_input_2,(0,0),fx= .30,fy= .30)
            
            ## face_recognition
            try:
              face_locations_1 = face_recognition.face_locations(image_input_1, number_of_times_to_upsample=0,model = "hog")
              face_encoding_1 = face_recognition.face_encodings(image_input_1,face_locations_1)[0]
              face_locations_2 = face_recognition.face_locations(image_input_2, number_of_times_to_upsample=0,model = "hog")
              face_encoding_2 = face_recognition.face_encodings(image_input_2, face_locations_2)[0]
            except IndexError:
                self.write("FACE WAS NOT FOUND")
            else:
           
              results = face_recognition.compare_faces([face_encoding_1], face_encoding_2,0.40)
              end = str(time.time() - start)
              if results[0]:
                  self.write("MATCHED" + end)
              else : 
                  self.write("NOT MATCHED" + end)

        except Exception as e:
            self.write(e)
        
if(__name__ == "__main__"):
    app = tornado.web.Application([
        ("/face/training", training),
        ("/", home),
        ("/face/delete", deleteid),
        ("/face/comparetwoface", comparetwoface),
        ("/face/whoisthat", whoisthat),
    ])
    app.listen(3455)
    print("on port 3455")

    tornado.ioloop.IOLoop.instance().start()
