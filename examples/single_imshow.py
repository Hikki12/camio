from camio import Camera
from threading import Event
import time
import cv2


readOk = Event()
image = None


def readFrame(frame):
    """Read frame callback."""
    global image
    image = frame
    readOk.set()


# Instance a camera object
camera = Camera(src='http://192.168.100.146:3000/video/mjpeg', fps=30, size=(320, 240))

# Setup callbacks
camera.on('frame-ready', readFrame)

# Start read loop in another thread
camera.start()


while True:
    t0 = time.time()
    if image is not None:
        cv2.imshow('image', image)
        readOk.clear()

    readOk.wait()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    t1 = time.time()
    dt = t1 - t0
    # print(f'dt: {dt: .4f} : {1/dt: .2f}')

camera.stop()
cv2.destroyAllWindows()