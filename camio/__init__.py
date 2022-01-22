import cv2
import time
import numpy as np
from typing import Union
from threading import Thread, Event, Lock
from .sevent import Emitter


class Camera(Emitter):
    """Camera device object, based on threading.
    :param src: device source
    :param name: device name
    :param reconnectDelay: wait time for try reopen camera device
    :param fps: frames per second
    :param verbose: display info messages?
    :param size: tuple or list with a dimension of the image
    :param emitterIsEnabled: disable on/emit events (callbacks execution)
    :param enableBackground: if some error is produced with the camera it will display a black frame with a message.
    Example usage::
        camera = Camera(src=0)
        camera.on('frame-ready', lambda frame: print('frame is ready:', type(frame)))
    """

    def __init__(
        self,
        src: Union[int, str] = 0,
        name: str = "default",
        reconnectDelay: Union[int, float] = 5,
        fps: Union[int, None] = 10,
        verbose: bool = False,
        size: Union[list, tuple, None] = None,
        emitterIsEnabled: bool = False,
        backgroundIsEnabled: bool = False,
        *args,
        **kwargs
    ):
        super(Camera, self).__init__(emitterIsEnabled=emitterIsEnabled)

        self.src = src
        self.name = name
        self.frame = None
        self.fps = fps
        self.verbose = verbose
        self.size = size
        self.backgroundIsEnabled = backgroundIsEnabled
        self.background = None

        if self.fps is not None:
            self.delay = 1 / self.fps
        else:
            self.delay = .1

        self.defaultDelay = self.delay    
        self.reconnectDelay = reconnectDelay
        self.defaultSize = [480, 640]

        self.emitterIsEnabled = emitterIsEnabled
        self.device = None
        self.thread = Thread(target=self.run, args=())

        self.runningEvent = Event()
        self.pauseEvent = Event()
        self.readEvent = Event()

        self.resume()

    def __del__(self):
        self.stop()

    def createBackground(
        self,
        text: str = "Device not available",
        font: None = cv2.FONT_HERSHEY_SIMPLEX,
        fontScale: Union[int, float] = 1,
        fontColor: Union[tuple, list] = [255, 255, 255],
        thickness: Union[int, float] = 1,
        size: Union[tuple, list, None] = None,
    ):
        """It creates a custom background as numpy array (image) with a text message.
        :param text: message to be displayed on the center of the background.
        :param font: cv2 font family
        :param fontScale: scale of the font
        :param fontColor: color of the font
        :param thickness: thickness of the font
        :param size: tuple, list with the size of the background. If it's None, size will be set automatically.        
        """
        if size is None:
            size = self.defaultSize
        w, h = size
        background = np.zeros(size)
        textsize = cv2.getTextSize(text, font, fontScale, thickness)[0]
        tw, th = textsize
        origin = (int((w - tw) / 2), int((h - th) / 2))
        background = cv2.putText(
            background, text, origin, font, fontScale, fontColor, thickness
        )
        return background

    def enableBackground(
        self,
        text: str = "Device not available.",
        font: None = cv2.FONT_HERSHEY_COMPLEX,
        fontScale: Union[int, float] = 1,
        fontColor: Union[tuple, list] = [255, 255, 255],
        thickness: Union[int, float] = 1,
        size: Union[tuple, list, None] = None,
    ):
        """It enables background as a frame.
        :param text: message to be displayed on the center of the background.
        :param font: cv2 font family
        :param fontScale: scale of the font
        :param fontColor: color of the font
        :param thickness: thickness of the font
        :param size: tuple, list with the size of the background. If it's None, size will be set automatically.
        """
        self.backgroundIsEnabled = True
        self.background = self.createBackground(
            text=text, font=font, fontScale=fontScale, fontColor=fontColor, thickness=thickness, size=size
        )

    def disableBackground(self):
        """It disables the background."""
        self.backgroundIsEnabled = False
        self.background = None

    def start(self):
        """It starts the read loop."""
        self.thread.start()
        return self

    def hasDevice(self) -> bool:
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

    def update(self):
        """It tries to read a frame from the camera."""
        self.readEvent.clear()

        deviceIsAvailable, frame = self.device.read()
        if deviceIsAvailable:
            self.frame = self.preprocess(frame)
            self.emit("frame-ready", self.frame)
            self.emit("frame-available", self.name)
        else:
            self.frame = self.getBackground()

        self.readEvent.set()

    def read(self) -> Union[None, np.ndarray]:
        """It returns a frame or a background."""
        if self.hasDevice():
            if self.readEvent.wait(timeout=0.1 * self.delay):
                return self.frame
        else:
            return self.background

    def applyDelay(self):
        """If a fps was defined it will wait for respective delay."""
        if self.fps is not None:
            time.sleep(self.delay)

    def run(self):
        """It runs the read loop."""
        self.loadDevice()
        self.runningEvent.set()
        while self.runningEvent.is_set():
            if self.hasDevice():
                self.update()
            else:
                self.reconnect()
            self.applyDelay()
            self.needAPause()
        self.device.release()

    def stop(self):
        """It stops the read loop."""
        self.runningEvent.clear()
        self.thread.join()

    def getName(self) -> str:
        """It returns the name of the current device."""
        return self.name

    def getFrame(self) -> Union[None, np.ndarray]:
        """It returns the current frame."""
        return self.frame

    def getBackground(self) -> Union[None, np.ndarray]:
        """It returns the current background."""
        return self.background

    def setSpeed(self, fps: Union[int, None] = 10):
        """It updates the frames per second (fps).

        :param fps: frames per second. If no parameter is passed, auto speed will be set.
        """
        self.fps = fps
        if self.fps is not None:
            self.defaultDelay = 1 / self.fps
            self.delay = self.defaultDelay


class Cameras:
    """A class for manage multiple threaded cameras.
    :param devices: a dict with names and sources of the camera devices.
    :param reconnectDelay: wait time for try reopen camera device
    :param fps: frames per second
    :param verbose: display info messages?
    :param size: tuple or list with a dimension of the image
    :param emitterIsEnabled: disable on/emit events (callbacks execution)
    :param enableBackground: if some error is produced with the camera it will display a black frame with a message.
    Example usage::
        hola()    
    """

    def __init__(self, 
        devices: dict = {}, 
        *args, 
        **kwargs):
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

    def startOnly(self, deviceName: str = "default"):
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

    def stopOnly(self, deviceName: str = "default"):
        """It stops an specific camera device.

        :param deviceName: camera device name.
        """
        if deviceName in self.devices:
            device = self.devices[deviceName]
            device.stop()

    def getDevice(self, deviceName: str = "default"):
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

    def setSpeedOnly(self, deviceName: str = "default", fps: int = 10):
        """It updates the FPS captured by a specific devices.

        :param deviceName: camera device name.
        """
        if deviceName in self.devices:
            self.devices[deviceName].setSpeed(fps)

    def getAllFrames(self, asDict=True):
        """It returns a list with all camera current frames.

        :param asDict: return frames as dict or as list?
        """
        if asDict:
            frames = {device.src: device.getFrame() for device in self.devices.values()}        
        else:
            frames = [device.getFrame() for device in self.devices.values()]
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
