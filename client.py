#!/usr/bin/env python

import time
import sys
import json
import argparse
import functools
import subprocess
import re
import websocket


# Detector map that holds the BCM GPIO pin to num_points mapping
DETECTOR_MAP = {
    4: 1,
    5: 1,
    6: 2,
    7: 2,
    8: 3,
}


class Client:
    def __init__(self, websocket_address, bounce_time):
        self._websocket_address = websocket_address
        self._bounce_time = bounce_time

        self._get_websocket_connection()
        self._status = {}

        self._setup_gpio()

    # Create the websocket connection
    def _get_websocket_connection(self):
        print "Establishing connection to %s" % self._websocket_address
        while True:
            print "Trying to connect to %s" % self._websocket_address
            try:
                self._websocket = websocket.create_connection(self._websocket_address)
                break
            except Exception as e:
                print "Failed to connect, retrying ..."
            time.sleep(1.0)
        print "Connected"

    def _setup_gpio(self):
        # Setup the GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(True)

        # Setup the detectors based on the detector map
        for gpio_pin, num_points in DETECTOR_MAP.iteritems():
            GPIO.setup(gpio_pin, GPIO.IN, GPIO.PUD_UP)
            GPIO.add_event_detect(gpio_pin, GPIO.FALLING, callback=functools.partial(
                self._sensor_triggered, num_points), bouncetime=self._bounce_time)

    @staticmethod
    def _get_wlan_status():
        try:
            out, err = subprocess.Popen(["iwconfig"], stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE).communicate()
        except OSError as e:
            return "unknown"

        essid = re.search('ESSID:"(.*?)"', out)
        quality = re.search('Link Quality=(\d+)/(\d+)\s*Signal level=(-?\d+) dBm', out)

        wlan_status = {
            "essid": essid.group(1) if essid else "",
            "link_quality": float(quality.group(1)) / float(quality.group(2)) if quality else float('nan'),
            "signal_level": float(quality.group(3)) if quality else float('nan')
        }

        return wlan_status

    def _update_status(self):
        self._status = {
            "wlan": self._get_wlan_status()
        }

    def _sensor_triggered(self, num_points, gpio_pin):
        data = {
            "time": time.time(),
            "status": self._status,
            "event": {
                "type": "sensor_reading",
                "data": {
                    "gpio_pin": gpio_pin,
                    "num_points": num_points
                }
            }
        }
        print "Sending data ...", data
        try:
            self._websocket.send(json.dumps(data))
        except Exception as e:
            print "Sending failed, trying to reconnect to socket ...", e
            self._get_websocket_connection()

    def spin(self):
        while True:
            self._update_status()
            time.sleep(1)
        self._websocket.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Camel race client")
    parser.add_argument("--websocket_address", help='Websocket server address', default='ws://localhost:3000', type=str)
    parser.add_argument("--bounce_time", help="GPIO bounce time in ms for sensor trigger", default=500, type=int)
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

    c = Client(args.websocket_address, args.bounce_time)
    c.spin()
