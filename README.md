# Python-CamIO

A library to handle multiple cameras with opencv, based on threading.

## Examples
```
from camio import MultipleCameras

camerasAdmin = MultipleCameras(devices={
    # 'deviceName': src
    'camera1': 0, 
    'camera2': 1
}, fps=5, reconnectDelay=5)

# Start all devices at once
camerasAdmin.startAll()

...

# Start all devices at once
camerasAdmin.startOnly('camera1')

# After of starting all devices you can do other tasks
my_task()

...

# get A frame
frame = camerasAdmin.getFrameOf('camera1')

...

# Get a list of frames
frames = camerasAdmin.getAllFrames()

...

# Pause All devices
camerasAdmin.pauseAll()

...

# Resume All devices
camerasAdmin.resumeAll()

...

# Pause one
camerasAdmin.pauseOnly('camera1')

# Resume one
camerasAdmin.resumeOnly('camera1')


```

## License
MIT