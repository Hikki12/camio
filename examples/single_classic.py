import cv2
from camio import Camera
import time


camera = Camera(src='http://192.168.100.146:3000/video/mjpeg', fps=10, size=(320, 240), classic=True)
camera.start()

while True:
    t0 = time.time()
    image = camera.read()

    if image is not None:
        cv2.imshow('image', image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    t1 = time.time()
    dt = t1 - t0
    print(dt)

camera.stop()
cv2.destroyAllWindows()