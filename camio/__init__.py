import cv2
import time
from threading import Thread, Event
from sevent import Emitter


class CameraDevice(Emitter):
    """Camera device object, based on threading.

    :param src: device source
    :param name: device name
    :param reconnectDelay: wait time for try reopen camera device
    :param fps: frames per second.
    """
    def __init__(self, src=0, name='default', reconnectDelay=2, fps=10, *args, **kwargs):
        super(CameraDevice, self).__init__()
        self.src = src
        self.name = name
        self.frame = None
        self.fps = fps
        self.delay = 1 / self.fps 
        self.defaultDelay = self.delay
        self.reconnectDelay = reconnectDelay
        self.device = None
        self.thread = Thread(target=self.run, args=())
        self.runningEvent = Event()
        self.pauseEvent = Event()
        self.resume()

    def __del__(self):
        self.stop()

    def start(self):
        """It starts the read loop."""
        self.thread.start()
    
    def hasDevice(self):
        """It checks if a camera device is available."""
        if self.device is not None:
            return self.device.isOpened()
        return False

    def loadDevice(self):
        """It loads a camera device."""
        try:
            self.device = cv2.VideoCapture(self.src)
        except Exception as e:
            self.device = None

    def reconnect(self):
        """It tries to reconnect with the camera device."""

        if not self.hasDevice():
            self.delay = self.reconnectDelay
            self.loadDevice()
            time.sleep(self.delay)

        if self.hasDevice():
            self.delay = self.defaultDelay

    def resume(self):
        """It resumes the read loop."""
        self.pauseEvent.set()

    def pause(self):
        """It pauses the read loop."""
        self.pauseEvent.clear()

    def needAPause(self):
        """It pauses or resume the read loop."""
        self.pauseEvent.wait()

    def readFrame(self):
        """It tries to read a frame from the camera."""
        try:
            status, frame = self.device.read()
            if status:
                self.frame = frame
                self.emit('frame-ready', frame)
            else:
                self.frame = None      
        except Exception as e:
            print(e)
            self.frame = None    

    def run(self):
        """It runs the read loop."""
        self.loadDevice()
        self.runningEvent.set()
        while self.runningEvent.is_set():
            if self.hasDevice():
                self.readFrame()
                time.sleep(self.delay)
            else:
                self.reconnect()     
            self.needAPause()

    def stop(self):
        """It stops the read loop."""
        self.runningEvent.clear()
        if self.hasDevice():
            self.device.release()

    def getFrame(self):
        """It returns the frame."""
        return self.frame

    def setSpeed(self, fps=10):
        """It updates the fps."""
        self.fps = fps
        self.defaultDelay = 1 / self.fps
        self.delay = self.defaultDelay


class MultipleCameras:
    def __init__(self,devices={}, *args, **kwargs):
        self.devices = {}
        if len(devices) > 0:
            for name, src in devices.items():
                self.devices[name] = CameraDevice(src, name=name, *args, **kwargs) 

    def __getitem__(self, name):
        return self.devices[name]

    def __len__(self):
        return len(self.devices)

    def startAll(self):
        for device in self.devices.values():
            device.start()

    def startOnly(self, deviceName:str="default"):
        if deviceName in self.devices:
            device = self.devices[deviceName]
            device.start()

    def stopAll(self):
        for device in self.devices.values():
            device.stop()
    
    def stopOnly(self, deviceName:str="default"):
        if deviceName in self.devices:
            device = self.devices[deviceName]
            device.stop()
    
    def getDevice(self, deviceName="default"):
        if deviceName in self.devices:
            return self.devices[deviceName]
        
    def pauseOnly(self, deviceName="default"):
        if deviceName in self.devices:
            device = self.devices[deviceName]
            device.pause()

    def pauseAll(self):
        for device in self.devices.values():
            device.pause()
    
    def resumeAll(self):
        for device in self.devices.values():
            device.resume()

    def resumeOnly(self, deviceName="default"):
        if deviceName in self.devices:
            device = self.devices[deviceName]
            device.resume()    

    def setSpeedOnly(self, deviceName="default", fps=10):
        if deviceName in self.devices:
            self.devices[deviceName] = fps
    
    def getAllFrames(self):
        frames = [device.getFrame() for device in self.devices.values]
        return frames

    def getFrameOf(self, deviceName="default"):
        if deviceName in self.devices:
            return self.devices[deviceName].getFrame()

