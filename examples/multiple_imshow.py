import cv2
from camio import Cameras


frames = {'camera1': None, 'camera2': None}

# Create a list of cameras with their corresponding sources
camerasAdmin = Cameras(devices={
    'camera1': 0,
    'camera2': 'http://192.168.100.146:3000/video/mjpeg'
}, fps=15, reconnectDelay=5, size=(320, 240))


def readFrames(device):
    global frames, camerasAdmin
    frames[device] = camerasAdmin.getFrameOf(device)


# Setup Callbacks
camerasAdmin.on('frame-available', readFrames)

# Starts all read loops for cameras in differents threads
camerasAdmin.startAll()

while True:

    frame1 = frames['camera1']
    frame2 = frames['camera2']

    if frame1 is not None and frame2 is not None:
        frame = cv2.hconcat([frame1, frame2])
        cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camerasAdmin.stopAll()
cv2.destroyAllWindows()
