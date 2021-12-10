# Python-CamIO

A library to handle multiple cameras with opencv, based on threading and callbacks.


## Single Camera
You could use a single camera with callbacks to do some image/video processing:
```python
from camio import Camera


def proccesVideo(frame):
    print(frame.shape)
    # Do some video processing
    # Or displays the frame
    # .
    # .


# Instance a camera object
camera = Camera(src=0, fps=10)

# Setup callbacks
camera.on('frame-ready', proccesVideo)

# Start read loop in another thread
camera.start()
```

## Multiple Cameras
Also, camIO can manage multiple cameras at the same time:

```python
from camio import Cameras


def frameAvailable(device):
    """Multiple cameras manager callback."""
    print(f"{device} has a new frame available")


# Create a list of cameras with their corresponding sources
camerasAdmin = Cameras(devices={
    'camera1': 0,
    'camera2': 1
}, fps=5, reconnectDelay=5)

# Setup Callbacks
camerasAdmin.on('frame-available', frameAvailable)

# Starts all read loops for cameras in differents threads
camerasAdmin.startAll()


```
And here are some extra functions for manage multiple cameras:
```python

from camio import Cameras

camerasAdmin = Cameras(devices={
    # 'deviceName': src
    'camera1': 0, 
    'camera2': 1
}, fps=5, reconnectDelay=5)

# Start all devices at once on separate threads
camerasAdmin.startAll()

...

# Start one single device on a separate thread
camerasAdmin.startOnly('camera1')

# After of starting all devices you can do other tasks
my_tasks()

...

# get a frame of a specific device
frame = camerasAdmin.getFrameOf('camera1')

...

# Get a list of all frames
frames = camerasAdmin.getAllFrames()

...

# Pause All devices
camerasAdmin.pauseAll()

...

# Resume All devices
camerasAdmin.resumeAll()

...

# Pause one specific device
camerasAdmin.pauseOnly('camera1')

# Resume one specific device
camerasAdmin.resumeOnly('camera1')

...

# Update all FPS(s) speed
camerasAdmin.setSpeed(fps=12)

# Update one specific FPS speed
camerasAdmin.setSpeedOnly('camera1', fps=5)

```

## License
MIT