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

