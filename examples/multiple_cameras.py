import cv2
import time
from camio import Cameras


devices = {
    'camera1': 0,
    'camera2': 'http://192.168.100.202:3000/video/mjpeg',
}

cameras = Cameras(
            devices=devices,
            fps=None,
            size=[400, 320],
            emitterIsEnabled=False,
            backgroundIsEnabled=True,
            queueModeEnabled=False
          )


cameras.startAll()


while True:
    frames = cameras.read(timeout=0.1, asDict=True)
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
