from camio import MultipleCameras

camerasAdmin = MultipleCameras(devices={
    'camera1': 0,
    'camera2': 1
}, fps=5, reconnectDelay=5)

camerasAdmin.startOnly('camera1')