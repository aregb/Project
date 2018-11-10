#!/usr/bin/env python
"""Created by Areg Babayan on 20/9/2018.
Copyright (C) 2018 Areg Babayan. ALl rights reserved."""
__author__      = "Areg Babayan"
__copyright__   = "Copyright (C) 2018 Areg Babayan"
__license__     = "BSD"
__version__     = "0.0.1"
__all__         = [] # why this?


import json
import time
import sys
import signal
import system.settings as settings
import system.environment as environment
from neural_presenters.serial.serial_communication import SerialInterface
#from neural_sources.file.file_server import FileServer
from neural_sources.server.client import Client
#from neural_interpreter.random_mode import RandomMode
from neural_interpreter.siren import Siren
from neural_interpreter.moving_average import MovingAverage
from neural_interpreter.support_functions.data_to_color import create_electrode_mapping
from neural_interpreter.eyes import Eyes
import rospy
from std_msgs.msg import String

_presenter = None
_source = None
_interpreter = None
_led_colors = None


#def callback(data):
#    rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)  #print to screen, rosout and log

def domecontrol():
    #rospy.Subscriber("/cyborg_led_dome/domecontrol", String, callback) #maa lage egen melidngstype aa bytte callback med
    #environment.setup(sys.argv[1:])
    global _led_colors, _presenter, _source, _interpreter
    _led_colors = bytearray([0] * (3 * settings.LEDS_TOTAL))
    _presenter = SerialInterface()

    def loop(data):
        global _interpreter, _presenter, _led_colors
        _interpreter.render(data, _led_colors)
        _presenter.refresh(_led_colors)

    
    
    _source = Client(loop, _presenter)
    _interpreter = MovingAverage()

    

    """frame_time = 1.0/settings.LED_REFRESHES_PER_SECOND
    neuron_data = [0] * settings.NEURAL_ELECTRODES_TOTAL
    while _presenter.running():
    while not rospy.is_shutdown():
        past_time = time.time()

        for i in range(len(neuron_data)):
            neuron_data[i] = 0
        loop(neuron_data)

        delta = time.time() - past_time
        sleep_time = frame_time - delta
        if sleep_time < 0:
            print("Can't keep up!")
            sleep_time = 0

        time.sleep(sleep_time)"""
    _source.loop()

    rospy.spin()

#if __name__ == '__main__':
#    environment.setup(sys.argv[1:])
#    listener()
