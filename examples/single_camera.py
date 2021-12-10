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