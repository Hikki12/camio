import cv2
from camio import Camera
import time


camera = Camera(src=0, fps=30, size=None, emitterIsEnabled=False)
camera.start()

while True:
    t0 = time.time()
    image = camera.read()

    if image is not None:
        cv2.imshow('image', image)
        print(image.shape)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    t1 = time.time()
    dt = t1 - t0
    # print(dt)

camera.stop()
cv2.destroyAllWindows()