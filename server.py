#!/usr/bin/env python
from flask import Flask
from flask_socketio import SocketIO, emit
import argparse
import sys
import functools
import time
import uuid

# Detector map that holds the BCM GPIO pin to player and num_points mapping
DETECTOR_MAP = [
    [(1, 1),    (2, 1),     (3, 2),     (4, 2),      (5, 2)],  # Player 1
    [(6, 1),    (7, 1),     (8, 2),     (9, 2),     (10, 2)],  # Player 2
    [(11, 1),   (12, 1),    (13, 2),    (14, 2),    (15, 2)],  # Player 3
    [(16, 1),   (17, 1),    (18, 2),    (19, 2),    (20, 2)],  # Player 4
    [(21, 1),   (22, 1),    (22, 2),    (23, 2),    (24, 2)],  # Player 5
]
RESET_GPIO_PIN = 25


class Server:
    def __init__(self, host, port, detector_bounce_time, reset_bounce_time):
        self._uuid = str(uuid.uuid4())
        self._host = host
        self._port = port
        self._detector_bounce_time = detector_bounce_time
        self._reset_bounce_time = reset_bounce_time

        self._setup_gpio()
        self._setup_socketio()

    def _setup_gpio(self):
        # Setup the GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(True)

        # Setup the detectors based on the detector map
        for idx, player_detectors in enumerate(DETECTOR_MAP):
            for gpio_pin, num_points in player_detectors:
                GPIO.setup(gpio_pin, GPIO.IN, GPIO.PUD_UP)
                GPIO.add_event_detect(gpio_pin, GPIO.FALLING, callback=functools.partial(
                    self._gpio_score_cb, idx, num_points), bouncetime=self._detector_bounce_time)

        # Setup reset button
        GPIO.setup(RESET_GPIO_PIN, GPIO.IN, GPIO.PUD_UP)
        GPIO.add_event_detect(RESET_GPIO_PIN, GPIO.FALLING, callback=self._gpio_reset_cb,
                              bouncetime=self._reset_bounce_time)

    def _setup_socketio(self):
        self._app = Flask(__name__)
        self._app.config['SECRET_KEY'] = 'secret!'
        self._socketio = SocketIO(self._app, async_mode=None)
        self._socketio.handlers.append(('connect', self._socketio_connect_cb))
        self._socketio.handlers.append(('disconnect', self._socketio_disconnect_cb))

    @staticmethod
    def _socketio_connect_cb():
        print "Connect"

    @staticmethod
    def _socketio_disconnect_cb():
        print "Disconnect"

    def _gpio_reset_cb(self, gpio_pin):
        self._socketio.emit('resetGame', gpio_pin)

    def _gpio_score_cb(self, player_id, num_points, gpio_pin):
        print "GPIO Score callback"
        msg = {
            "origin": "{}-player-{}".format(self._uuid, player_id),
            "numPoints": num_points,
            "gpioPin": gpio_pin
        }
        self._socketio.emit('score', msg)

    def run(self):
        self._socketio.run(self._app, host=self._host, port=self._port)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Camel race client")
    parser.add_argument("--host", help='SocketIO address', default='localhost', type=str)
    parser.add_argument("--port", help='SocketIO server port', default=3000, type=int)
    parser.add_argument("--detector-bounce_time", help="GPIO bounce time in ms for detectors", default=500, type=int)
    parser.add_argument("--reset-bounce_time", help="GPIO bounce time in ms for reset button", default=500, type=int)
    parser.add_argument("--stub", action="store_true")
    args = parser.parse_args()

    if args.stub:
        from gpio_stub import GPIO
    else:
        try:
            import RPi.GPIO as GPIO
        except ImportError as e:
            print "Failed to import Raspberry PI GPIO, try running with --stub on a non-raspberry pi platform"
            sys.exit(1)

    server = Server(args.host, args.port, args.detector_bounce_time, args.reset_bounce_time)
    server.run()
