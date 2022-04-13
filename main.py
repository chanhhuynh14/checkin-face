import cv2
import face_recognition
import json
import time

list_id_facedata= []
list_face_facedata = []
list_user_matching = []
frame_rate = 5
prev = 0
with open('facedata.json') as f:
  data = json.load(f)
for person in data["People"]:
  list_id_facedata.append(person["id"])
  list_face_facedata.append(person["face"])

with open('username.json') as f:
    list_user_matching = json.load(f)

#video = cv2.VideoCapture("rtsp://admin:@192.168.100.16:554")
video = cv2.VideoCapture("/home/it/Desktop/AntiFake/video/real.mov")
def change_res(width, height):
    video.set(3, width)
    video.set(4, height)


def rescale_frame(frame, percent=65):
    width = int(frame.shape[1] * percent/ 100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)

change_res(480,220)

while True :
    time_elapsed = time.time() - prev
    ret, frame = video.read()
    smallFrame = cv2.resize(frame,(0,0),fx= .25,fy= .25)
    smallFrameRGB = smallFrame[:,:,::-1]
    if time_elapsed > 1./frame_rate:
        prev = time.time()
        face_locations = face_recognition.face_locations(smallFrameRGB , number_of_times_to_upsample=0, model = "hog")   
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
            cv2.putText(frame, name, (left*4, top*4 - 6), cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 255), 2)
    cv2.imshow("eID", rescale_frame(frame))
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break
    
video.release()
cv2.destroyAllWindows
