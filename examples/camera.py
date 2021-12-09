from camio import CameraDevice

camera = CameraDevice(src=0)
camera.start()
camera.on('frame-ready', lambda frame: print(len(frame)))