import thread
import time
import random


_gpio_thread_running = False
_callbacks = []


def gpio_thread():
    while True:
        time.sleep(random.random() * 4)  # Sleep somewhere between 0 ... 4
        gpio_pin, callback = random.choice(_callbacks)
        callback(gpio_pin)


def _setup_callback(gpio_pin, callback):
    global _gpio_thread_running, _callbacks

    _callbacks.append((gpio_pin, callback))

    if not _gpio_thread_running:
        thread.start_new_thread(gpio_thread, ())
        _gpio_thread_running = True


class GPIO:
    BCM = 0
    IN = 0
    PUD_UP = 0
    FALLING = 0

    def __init__(self):
        pass

    @staticmethod
    def setmode(value):
        pass

    @staticmethod
    def setwarnings(value):
        pass

    @staticmethod
    def setup(gpio_pin, val1, val2):
        pass

    @staticmethod
    def add_event_detect(gpio_pin, val1, callback, bouncetime=0):
        _setup_callback(gpio_pin, callback)
