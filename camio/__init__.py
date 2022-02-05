import cv2
import time
import numpy as np
from typing import Union
from queue import Queue
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
    :param enableBackground: if some error is produced with the camera it will display
                             a black frame with a message.
    :param queueModeEnabled: enable queue mode?
    :param queueMaxSize: queue maxsize

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
        queueModeEnabled: bool = False,
        queueMaxSize: int = 96,
        text: str = "Device not available",
        font: None = cv2.FONT_HERSHEY_SIMPLEX,
        fontScale: Union[int, float] = .5,
        fontColor: Union[tuple, list] = [255, 255, 255],
        thickness: int = 1,
        *args,
        **kwargs
    ):
        super(Camera, self).__init__(emitterIsEnabled=emitterIsEnabled, *args, **kwargs)
        self.src = src
        self.name = name
        self.frame = None
        self.fps = fps
        self.verbose = verbose
        self.size = size
        self.backgroundIsEnabled = backgroundIsEnabled
        self.background = None
        self.queueModeEnabled = queueModeEnabled
        self.queue = Queue(maxsize=queueMaxSize)

        if self.fps is not None:
            self.delay = 1 / self.fps
        else:
            self.delay = .1

        self.defaultDelay = self.delay
        self.reconnectDelay = reconnectDelay
        self.defaultSize = [720, 1280, 3]

        self.emitterIsEnabled = emitterIsEnabled
        self.device = None
        self.thread = Thread(target=self.run, args=())

        self.runningEvent = Event()
        self.pauseEvent = Event()
        self.readEvent = Event()
        self.readLock = Lock()

        self.resume()

        if self.backgroundIsEnabled:
            self.enableBackground(
                size=self.size,
                text=text, font=font,
                fontColor=fontColor,
                fontScale=fontScale,
                thickness=thickness
            )

    def __del__(self):
        self.stop()

    def createBackground(
        self,
        text: str = "Device not available",
        font: None = cv2.FONT_HERSHEY_SIMPLEX,
        fontScale: Union[int, float] = .5,
        fontColor: Union[tuple, list] = [255, 255, 255],
        thickness: int = 1,
        size: Union[tuple, list, None] = None,
    ):
        """It creates a custom background as numpy array (image) with a text message.
        :param text: message to be displayed on the center of the background.
        :param font: cv2 font family
        :param fontScale: scale of the font
        :param fontColor: color of the font
        :param thickness: thickness of the font
        :param size: tuple, list with the size of the background.
                     If it's None, size will be set automatically.
        """
        if size is None:
            size = self.defaultSize

        if len(size) == 2:
            size = size[::-1]
            size.append(3)

        background = np.zeros(size, dtype=np.uint8)
        textsize = cv2.getTextSize(text, font, fontScale, thickness)[0]
        h, w, _ = size
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
        fontScale: Union[int, float] = 2,
        fontColor: Union[tuple, list] = [255, 255, 255],
        thickness: int = 3,
        size: Union[tuple, list, None] = None,
    ):
        """It enables background as a frame.
        :param text: message to be displayed on the center of the background.
        :param font: cv2 font family
        :param fontScale: scale of the font
        :param fontColor: color of the font
        :param thickness: thickness of the font
        :param size: tuple, list with the size of the background. If it's None,
                     size will be set automatically.
        """
        self.backgroundIsEnabled = True
        self.background = self.createBackground(
            text=text, font=font, fontScale=fontScale,
            fontColor=fontColor, thickness=thickness,
            size=size
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
        try:
            self.device = cv2.VideoCapture(self.src)
        except cv2.error as e:
            print('Exception: ', e)

    def reconnect(self):
        """It tries to reconnect with the camera device."""
        self.readEvent.clear()
        self.loadDevice()
        time.sleep(self.reconnectDelay)
        self.readEvent.set()

    def resume(self):
        """It resumes the read loop."""
        self.pauseEvent.set()

    def pause(self):
        """It pauses the read loop."""
        self.pauseEvent.clear()

    def needAPause(self):
        """It pauses or resume the read loop."""
        self.pauseEvent.wait()

    def preprocess(self, frame) -> np.ndarray:
        """It preprocess the frame."""
        if self.size is not None:
            frame = cv2.resize(frame, self.size[:2])
        return frame

    def update(self):
        """It tries to read a frame from the camera."""
        self.readEvent.clear()
        self.readLock.acquire()

        deviceIsAvailable, frame = self.device.read()
        if deviceIsAvailable:
            self.frame = self.preprocess(frame)

            if self.emitterIsEnabled:
                self.emit("frame-ready", self.frame)
                self.emit("frame-available", self.name)

            if self.queueModeEnabled:
                self.queue.put(self.frame)

        self.readEvent.set()
        self.readLock.release()

    def read(self, timeout: Union[float, int, None] = 0) -> Union[None, np.ndarray]:
        """It returns a frame or a background.

        :param timeout: max time in seconds to lock operation
        """
        if self.hasDevice():
            while self.queueModeEnabled:
                return self.queue.get(timeout=timeout)
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

        self.queueModeEnabled = False
        self.readEvent.set()
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
        if self.backgroundIsEnabled:
            if self.background is None:
                self.background = self.createBackground(size=self.size)
            return self.background

    def setSpeed(self, fps: Union[int, None] = 10):
        """It updates the frames per second (fps).

        :param fps: frames per sec. If no parameter is passed, auto speed will be set.
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
    :param enableBackground: if some error is produced with the camera it will display
                             a black frame with a message.
    Example usage::
        cameras = Cameras(devices={'camera1': 0, 'cameras2': 1})
    """

    def __init__(
            self,
            devices: dict = {},
            *args,
            **kwargs):
        self.devices = {}
        if len(devices) > 0:
            for name, src in devices.items():
                if isinstance(src, dict):
                    self.devices[name] = Camera(name=name, **src)
                else:
                    self.devices[name] = Camera(src=src, name=name, *args, **kwargs)

    def __getitem__(self, name):
        return self.devices[name]

    def __len__(self):
        return len(self.devices)

    def startAll(self):
        """It starts all camera devices on the devices dict."""
        for device in self.devices.values():
            device.start()

    def startOnly(self, deviceName: str = "default"):
        """It starts only a specific device.

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
        """It returns a list with all cameras current frames.

        :param asDict: return frames as dict or as list?
        """
        if asDict:
            frames = {
                        device.getName(): device.getFrame()
                        for device in self.devices.values()
            }
        else:
            frames = [device.getFrame() for device in self.devices.values()]
        return frames

    def getFrameOf(self, deviceName="default"):
        """It returns a specific frame of a camera device.
        :param deviceName: camera device name.
        """
        if deviceName in self.devices:
            return self.devices[deviceName].getFrame()

    def read(self, timeout=0, asDict=True):
        """It returns a list or a dict of frames/backgrounds.
        :param timeout: max wait time in seconds.
        :param asDict: return as a dict?
        """
        if asDict:
            return {
                    device.getName(): device.read(timeout=timeout)
                    for device in self.devices.values()
            }
        else:
            return [device.read(timeout=timeout) for device in self.devices.values()]

    def on(self, *args, **kwargs):
        for device in self.devices.values():
            device.on(*args, **kwargs)
