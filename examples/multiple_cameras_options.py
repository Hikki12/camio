import cv2
import time
from camio import Cameras


devices = {
    'camera1': {
        'src': 0,
        'fps': None,
        'size': [320, 240],
        'backgroundIsEnabled': True,
        'emitterIsEnabled': False,
        'queueModeEnabled': False,
        'queueMaxSize': 32,
    },
    'camera2': {
        'src': 'http://192.168.100.202:3000/video/mjpeg',
        'fps': None,
        'size': [320, 240],
        'backgroundIsEnabled': True,
        'emitterIsEnabled': False,
        'queueModeEnabled': False,
        'queueMaxSize': 96,
    },
}


cameras = Cameras(devices=devices)
cameras.startAll()


while True:
    frames = cameras.read(timeout=0.2, asDict=True)
    frame1, frame2 = frames['camera1'], frames['camera2']
    if frame1 is not None and frame2 is not None:
        try:
            frame = cv2.hconcat([frame1, frame2])
            cv2.imshow('frame', frame)
        except Exception as e:
            print(e)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(.05)
cameras.stopAll()
cv2.destroyAllWindows()
