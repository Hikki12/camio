import cv2
import time
import numpy as np
from threading import Thread, Event
from .sevent import Emitter


class Camera(Emitter):
    """Camera device object, based on threading.

    :param src: device source
    :param name: device name
    :param reconnectDelay: wait time for try reopen camera device
    :param fps: frames per second.

    Example usage::

        camera = Camera(src=0)
        camera.on('frame-ready', lambda frame: print('frame is ready:', type(frame)))

    """
    def __init__(self, src=0, name='default', reconnectDelay=5, fps=10, verbose=False, size=None, classic=False, *args, **kwargs):
        super(Camera, self).__init__()
        self.src = src
        self.name = name
        self.frame = None
        self.fps = fps
        self.verbose = verbose
        self.delay = 1 / self.fps 
        self.defaultDelay = self.delay
        self.reconnectDelay = reconnectDelay
        self.size = size
        self.background = self.createBackground()

        self.classic = classic
        self.device = None
        self.thread = Thread(target=self.run, args=())
        self.runningEvent = Event()
        self.pauseEvent = Event()
        self.readEvent = Event()
        self.resume()

    def __del__(self):
        self.stop()

    def createBackground(self, text='Device not available'):
        size = self.size
        if self.size is None:
            size = (320, 240)
        w, h = size
        background = np.zeros(self.size)
        font = cv2.FONT_HERSHEY_SIMPLEX
        color = [255, 255, 255]
        fontScale = 1
        thickness = 1
        textsize = cv2.getTextSize(text, font, fontScale, thickness)[0]
        tw, th = textsize
        origin = (int((w - tw) / 2), int((h - th) / 2))
        background = cv2.putText(background, text, origin, font, fontScale, color, thickness)
        return background

    def start(self, classic=False):
        """It starts the read loop.

        :param classic: start camera device disabling all event/emit functions?
        """
        self.thread.start()
        if self.classic:
            self.disableEvents()
        return self
    
    def hasDevice(self):
        """It checks if a camera device is available."""
        if self.device is not None:
            return self.device.isOpened()
        return False

    def loadDevice(self):
        """It loads a camera device."""
        self.device = cv2.VideoCapture(self.src)

    def reconnect(self):
        """It tries to reconnect with the camera device."""
        self.readEvent.set()
        self.loadDevice()

    def resume(self):
        """It resumes the read loop."""
        self.pauseEvent.set()

    def pause(self):
        """It pauses the read loop."""
        self.pauseEvent.clear()

    def needAPause(self):
        """It pauses or resume the read loop."""
        self.pauseEvent.wait()

    def preprocess(self, frame):
        if self.size is not None:
            frame = cv2.resize(frame, self.size)
        return frame

    def readFrame(self):
        """It tries to read a frame from the camera."""
        self.readEvent.clear()
        status, frame = self.device.read()
        if status:
            frame = self.preprocess(frame)
            self.frame = frame
            self.emit('frame-ready', frame)
            self.emit('frame-available', self.name)
        else:
            self.frame = self.background  
        self.readEvent.set()    

    def read(self):
        if self.hasDevice():
            if self.readEvent.wait(timeout=0.1 * self.delay):
                return self.frame
        else:
            return self.background

    def run(self):
        """It runs the read loop."""
        self.loadDevice()
        self.runningEvent.set()
        while self.runningEvent.is_set():
            if self.hasDevice():
                self.readFrame()
            else:
                self.reconnect()
            time.sleep(self.delay)     
            self.needAPause()
        self.device.release()

    def stop(self):
        """It stops the read loop."""
        self.runningEvent.clear()
        self.thread.join()

    def getFrame(self):
        """It returns the frame."""
        return self.frame

    def setSpeed(self, fps=10):
        """It updates the fps."""
        self.fps = fps
        self.defaultDelay = 1 / self.fps
        self.delay = self.defaultDelay


class Cameras:
    """A class for manage multiple threaded cameras.

    :param devices: a dict with names and sources of the camera devices.
    """
    def __init__(self, devices:dict={}, *args, **kwargs):
        self.devices = {}
        if len(devices) > 0:
            for name, src in devices.items():
                self.devices[name] = Camera(src, name=name, *args, **kwargs) 

    def __getitem__(self, name):
        return self.devices[name]

    def __len__(self):
        return len(self.devices)

    def startAll(self):
        """It starts all camera devices on the devices dict."""
        for device in self.devices.values():
            device.start()

    def startOnly(self, deviceName:str="default"):
        """It start only a specific device.
        
        :param deviceName: camera device name.
        """
        if deviceName in self.devices:
            device = self.devices[deviceName]
            device.start()

    def stopAll(self):
        """It stops all camera devices."""
        for device in self.devices.values():
            device.stop()
    
    def stopOnly(self, deviceName:str="default"):
        """It stops an specific camera device.
        
        :param deviceName: camera device name.
        """
        if deviceName in self.devices:
            device = self.devices[deviceName]
            device.stop()
    
    def getDevice(self, deviceName:str="default"):
        """It returns a specific camera device.

        :param deviceName: camera device name.
        """
        if deviceName in self.devices:
            return self.devices[deviceName]
        
    def pauseOnly(self, deviceName="default"):
        """It pauses a specific camera device.

        :param deviceName: camera device name.
        """
        if deviceName in self.devices:
            device = self.devices[deviceName]
            device.pause()

    def pauseAll(self):
        """It pauses all camera devices."""
        for device in self.devices.values():
            device.pause()
    
    def resumeAll(self):
        """It resumes all camera devices."""
        for device in self.devices.values():
            device.resume()

    def resumeOnly(self, deviceName="default"):
        """It resumes a specific camera device.

        :param deviceName: camera device name.
        """
        if deviceName in self.devices:
            device = self.devices[deviceName]
            device.resume()    

    def setSpeedOnly(self, deviceName:str="default", fps:int=10):
        """It updates the FPS captured by a specific devices.
        
        :param deviceName: camera device name.
        """
        if deviceName in self.devices:
            self.devices[deviceName].setSpeed(fps)
    
    def getAllFrames(self, asDict=True):
        """It returns a list with all camera current frames."""
        if not asDict:
            frames = [device.getFrame() for device in self.devices.values()]
        else:
            frames = {device.src: device.getFrame() for device in self.devices.values()}
        return frames

    def getFrameOf(self, deviceName="default"):
        """It returns a specific frame of a camera device.

        :param deviceName: camera device name.
        """
        if deviceName in self.devices:
            return self.devices[deviceName].getFrame()

    def on(self, *args, **kwargs):
        for device in self.devices.values():
            device.on(*args, **kwargs)
