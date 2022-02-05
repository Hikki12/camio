# Examples

## Single camera
```python
import time
import cv2
from camio import Camera


camera = Camera(
            src=0, 
            fps=30, 
            size=None, 
            emitterIsEnabled=False,
            queueModeEnabled=False,
            backgroundIsEnabled=True,
        )

camera.start()

while True:
    image = camera.read()

    if image is not None:
        cv2.imshow('image', image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.stop()
cv2.destroyAllWindows()
```