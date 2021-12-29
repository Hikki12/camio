import cv2
from camio import Cameras
import time


camerasAdmin = Cameras(devices={
    'camera1': 0,
    'camera2': 'http://192.168.100.146:3000/video/mjpeg'
}, fps=30, reconnectDelay=5, size=(320, 240))

camerasAdmin.startAll()

while True:
    frames = camerasAdmin.getAllFrames(asDict=False)
    try:
        frame = cv2.hconcat(frames)  
        cv2.imshow('frame', frame)
    except:
        pass

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break   

    # time.sleep(.1)

camerasAdmin.stopAll()
cv2.destroyAllWindows()