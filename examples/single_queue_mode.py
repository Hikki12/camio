import cv2
from camio import Camera


camera = Camera(
            src=0,  # set a source
            fps=None,  # Automatic set fps
            size=None,  # Automatic set of the size resolution
            emitterIsEnabled=False,  # Disable callbacks
            backgroundIsEnabled=True,  # Enable background
            queueModeEnabled=True,  # Enable queue mode
        )

camera.start()

while True:
    image = camera.read(timeout=None)
    if image is not None:
        cv2.imshow('image', image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.stop()
cv2.destroyAllWindows()
