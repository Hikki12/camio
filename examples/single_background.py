import cv2
from camio import Camera


camera = Camera(
            src=3,  # set a source that does not exists.
            fps=None,  # Automatic set fps
            size=None,  # Automatic set of the size resolution
            emitterIsEnabled=False,  # Disable callbacks
            backgroundIsEnabled=True,  # Enable Background
            queueModeEnabled=False,  # Disable queue mode
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
