import cv2
import numpy as np
import face_recognition

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
#
while True:
    ret, frame = cap.read()
    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    img_small = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
    img_small = cv2.flip(img_small, 1)
    rgb_smaill_frame = img_small[:, :, ::-1]
    face_locations = face_recognition.face_locations(img_small)
    face_encodings = face_recognition.face_encodings(rgb_smaill_frame, face_locations)
    print(face_locations)
    
    cv2.imshow("WebCam" ,img_small)
    if cv2.waitKey(5) == ord('q') and face_encodings:
        break

cv2.destroyAllWindows()
print(face_encodings)
