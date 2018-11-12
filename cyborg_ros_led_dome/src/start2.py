 #!/usr/bin/env python
"""Created by Areg Babayan on 20/9/2018.
Copyright (C) 2018 Areg Babayan. ALl rights reserved."""
__author__      = "Areg Babayan"
__copyright__   = "Copyright (C) 2018 Areg Babayan"
__license__     = "BSD"
__version__     = "0.0.2"
__all__         = [] # why this?


import rospy
import time
#import sys
import system.settings as settings
#import copy from deepcopy
from neural_presenters.serial.serial_communication import SerialInterface
from neural_interpreter.siren import Siren
from neural_sources.file.file_server import FileServer
from neural_sources.server.client import Client
from neural_interpreter.individual_moving_average import IndividualMovingAverage
from neural_interpreter.moving_average import MovingAverage
from cyborg_ros_led_dome.msg import LedDomeControl
from neural_interprete.eyes import Eyes

class Domecontrol():

    _presenter = SerialInterface()
    _interpreter = Siren()
    _led_colors = bytearray([0] * (3 * settings.LEDS_TOTAL))
    _source = None
    mode_msg = LedDomeControl()

    neuron_data = [0] * settings.NEURAL_ELECTRODES_TOTAL

    def loop(neural_data):
        global _interpreter, _presenter, _led_colors
        rospy.Subscriber("LedDomeControl", LedDomeControl,callback) #husk å sette topic
        _interpreter.render(neural_data, _led_colors)
        _presenter.refresh(_led_colors)

    def change_mode(msg):
        global _interpreter, _presenter, _led_colors,_source,_change_requested
        settings.NEURAL_SOURCE = msg.source
        settings.NEURAL_INTERPRETER = msg.interpreter
        settings.NEURAL_DATA_TYPE = msg.data_type
        settings.NEURAL_DATA_FILE = msg.data_file

        if settings.NEURAL_SOURCE == "none": #kanskje fordel å sjekke source
            _source = None
            if settings.NEURAL_INTERPRETER == "siren":
                _interpreter = Siren()
            elif settings.NEURAL_INTERPRETER == "eyes":
                _interpreter = Eyes()
            else:
                #error handling
                pass
        else:
            if settings.NEURAL_SOURCE == "file":
                _source = FileServer(loop,_presenter)
            elif settings.NEURAL_SOURCE =="server":
                _source = Client(loop,_presenter)
            else:
                #error handling
                pass
            if settings.NEURAL_INTERPRETER == "individual-moving-average":
                _interpreter = IndividualMovingAverage()
            elif settings.NEURAL_INTERPRETER == "moving-average":
                _interpreter = MovingAverage()
            else:
                #error handling
                pass


    def callback(data):
        rospy.loginfo(rospy.get_caller_id(),data)
        global mode_msg = deeepcopy(data)
        settings.CHANGE_REQUESTED = True

    while not rospy.is_shutdown(): #sett begge loops inn her, sjekkk med change_requested
         if _source is None:
             while not settings.CHANGE_REQUESTED:
                 neuron_data = [0] * settings.NEURAL_ELECTRODES_TOTAL
                 for i in range(len(neuron_data)):
                 neuron_data[i] = 0
                 loop(neuron_data)
         else:
             _source.loop()

         change_mode(mode_msg)
         settings.CHANGE_REQUESTED = False
