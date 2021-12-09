"""
Taken from: https://github.com/Hikki12/sevent
"""

class Emitter:
    """This class implements a simple event emitter.
    
    Example usage::

        callback = lambda message: print(message)

        event = Emitter() 
        event.on('ready', callback)
        event.emit('ready', 'Finished!')
    """
    def __init__(self, *args, **kwargs):
        self.callback = None
        self.callbacks = {}

    def on(self, eventName:str, callback):
        """It sets the callback functions.

        :param eventName: name of the event
        :param callback: function
        """
        if self.callbacks is None:
            self.callbacks = {}
        if eventName not in self.callbacks:
            self.callbacks[eventName] = [callback]
        else:
            self.callbacks[eventName].append(callback)

    def emit(self, eventName:str, *args, **kwargs):
        """It emits an event, and calls the corresponding callback function.

        :param eventName: name of the event.
        """
        if self.callbacks is not None and eventName in self.callbacks:
            for callback in self.callbacks[eventName]:
                if callback.__code__.co_argcount > 0:
                    callback(*args, **kwargs)
                else:
                    callback()

    def clearEvent(self, eventName:str):
        """It clears the callbacks associated to a specific event name.

        :param eventName: name of the event.
        """
        if eventName in self.callbacks:
            del self.callbacks[eventName]
