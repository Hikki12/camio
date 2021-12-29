from camio import Camera


def proccesVideo(frame):
    print(frame.shape)

# Instance a camera object
camera = Camera(src=0, fps=30)

# Setup callbacks
camera.on('frame-ready', proccesVideo)

# Start read loop in another thread
camera.start()