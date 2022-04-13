from threading import Thread
from imutils.video import FPS
from imutils.video import FileVideoStream
import time
import sys
import cv2
import face_recognition
import json


list_id_facedata= []
list_face_facedata = []
list_user_matching = []

if sys.version_info >= (3,0):
    from queue import Queue
else:
    from Queue import Queue

with open('facedata.json') as f:
  data = json.load(f)
for person in data["People"]:
  list_id_facedata.append(person["id"])
  list_face_facedata.append(person["face"])
with open('username.json') as f:
    list_user_matching = json.load(f)

class FileVideoStream:
    def __init__(self, path,queueSize = 128):
        self.stream = cv2.VideoCapture(path)
        self.stopped = False
        self.Q = Queue(maxsize= queueSize)
    def start(self):
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self
    def update(self):
        while True:
            if self.stopped:
                return
            if not self.Q.full():
                (grabbed, frame) = self.stream.read()

                if not grabbed:
                    self.stop()
                    return
                self.Q.put(frame)
    def read(self):
        return self.Q.get()
    def more(self):
        return self.Q.qsize() > 0
    def stop(self):
        self.stopped = True

print("Starting video file thread..")
fvs = FileVideoStream("rtsp://admin:@192.168.10.110:554").start()
time.sleep(1.0)
fps = FPS().start()

def change_res(width, height):
    fvs.set(3, width)
    fvs.set(4, height)
def rescale_frame(frame, percent=75):
    width = int(frame.shape[1] * percent/ 100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)

#change_res(480,220)

while fvs.more() :
    frame = fvs.read()
    smallFrame = cv2.resize(frame,(0,0),fx= .25,fy= .25)
    smallFrameRGB = smallFrame[:,:,::-1]
    face_locations = face_recognition.face_locations(smallFrameRGB , number_of_times_to_upsample=0, model = "cnn")   
    face_encodings = face_recognition.face_encodings(smallFrameRGB, face_locations)

    for (top,right,bottom,left), face_encoding in zip(face_locations,face_encodings):
        matches = face_recognition.compare_faces(list_face_facedata, face_encoding,0.35)
        name = "Unknown" 

        if True in matches:
             first_match_index = matches.index(True)
             for person in list_user_matching["Users"]:
                if(person["id"] == list_id_facedata[first_match_index]):
                  name =  person["name"]

        cv2.rectangle(frame, (left*4, top*4), (right*4, bottom*4),(255, 0, 0), 3)
        cv2.putText(frame, name, (left*4, top*4 - 6), cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0), 2)
    
    cv2.imshow("eID", rescale_frame(frame))
    key = cv2.waitKey(1) & 0xFF
    fps.update()
    if key == ord('q'):
        break

fps.stop()
print("Elapsed time :{:.2f}".format(fps.elapsed()))
print("Approx. FPS :{:.2f}".format(fps.fps()))

cv2.destroyAllWindows
fvs.stop()
