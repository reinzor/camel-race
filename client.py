#!/usr/bin/env python

import time
import sys
import json

from functools import partial
import RPi.GPIO as GPIO

import subprocess
import re

from websocket import create_connection


if len(sys.argv) < 3:
	print "Usage: ./client.py [websocket_address (e.g. ws://localhost:3000)] [bouncetime (e.g. 500)]"
	sys.exit(1)
	
# Read and parse the input args
program, WEBSOCKET_ADDRESS, bounce_time = sys.argv
bounce_time = int(bounce_time)

# Create the websocket connection
def get_websocket_connection():
    print "Establishing connection to %s" % WEBSOCKET_ADDRESS
    while True:
        print "Trying to connect to %s" % WEBSOCKET_ADDRESS
        try:
            ws = create_connection(WEBSOCKET_ADDRESS)
            break
        except Exception as e:
            print "Failed to connect, retrying ..."
        time.sleep(1.0)
    print "Connected"
    return ws
    
# Initialy connect to the server
WS = get_websocket_connection()

# Setup the GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(True)

# Detector map that holds the BCM GPIO pin to num_points mapping
DETECTOR_MAP = {
  4: 1,
  5: 1,
  6: 2,
  7: 2,
  8: 3,
}

# Keep track of the system status
STATUS = {}

# Request the wlan status using iwconfig
def get_wlan_status():
	out, err = subprocess.Popen(["iwconfig"], stdout=subprocess.PIPE, 
	                            stderr=subprocess.PIPE).communicate()
	                            	
	essid = re.search('ESSID:"(.*?)"', out)
	quality = re.search('Link Quality=(\d+)/(\d+)\s*Signal level=(-?\d+) dBm', out)
	
	wlan_status = {}
	wlan_status["essid"] = essid.group(1) if essid else ""
	wlan_status["link_quality"] = float(quality.group(1)) / int(quality.group(2)) if quality else 0
	wlan_status["signal_level"] = int(quality.group(3)) if quality else ""
			
	return wlan_status


# Fetch the system status
def fetch_status():
	global STATUS
	STATUS = {
	  "wlan": get_wlan_status()
	}


# Callback fired when a ball is detected
def detected(num_points, gpio_pin):
    global WS
    
    data = {
      "time": time.time(),
      "status": STATUS,
      "event": {
            "gpio_pin": gpio_pin,
            "num_points": num_points  
        }
    }
    print "Sending data ...", data
    try:
        WS.send(json.dumps(data))
    except:
        print "Sending failed, trying to reconnect to socket ..."
        WS = get_websocket_connection()


# Setup the detectors based on the detector map
for gpio_pin, num_points in DETECTOR_MAP.iteritems():
    GPIO.setup(gpio_pin, GPIO.IN, GPIO.PUD_UP)
    GPIO.add_event_detect(gpio_pin, GPIO.FALLING, 
                          callback=partial(detected, num_points), bouncetime=bounce_time)                    

print "GPIO pins are set-up, spinning ..."

# Spin the client and periodically fetch the status
while True:
    fetch_status()
    time.sleep(0.1)
    
WS.close()
