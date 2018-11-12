#!/usr/bin/env python
"""Created by Areg Babayan on 6/10/2018."""
__author__      = "Areg Babayan"
__license__     = "BSD"
__version__     = "0.0.4"


import rospy
import system.settings as settings
import smach
from std_msgs.msg import String
import time
from neural_presenters.serial.serial_communication import SerialInterface
from neural_interpreter.random_mode import RandomMode
from neural_interpreter.siren import Siren
from neural_interpreter.support_functions.data_to_color import create_electrode_mapping
from neural_interpreter.eyes import Eyes
from neural_interpreter.moving_average import MovingAverage
from neural_interpreter.intensity import Intensity
from neural_sources.file.file_server import FileServer
from neural_sources.server.client import Client

#_presenter = None
#_source = None
#_interpreter = None
#_led_colors = None
#_next_mode = None 
#_current_mode = None #set default start here

def callback(data,args):
    #rospy.loginfo(rospy.get_caller_id()+ "domecontrol", data.data)
    args = data.data #set next_mode
    #_next_mode = data.data
    print("next mode: %s"%args)
    settings.CHANGE_REQUESTED = True

""" def loop(data):
    global _interpreter, _presenter, _led_colors
    _interpreter.render(data, _led_colors)
    _presenter.refresh(_led_colors)
 """
class startup(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=["transition"],
                            #input_keys=["presenter_in","interpreter_in","led_colors_in"],
                            output_keys=["presenter_out","interpreter_out","led_colors_out","current_mode_out"])
        self.neuron_data = [0] * settings.NEURAL_ELECTRODES_TOTAL
        settings.CHANGE_REQUESTED = False
    
    def execute(self,userdata):
        userdata.led_colors_out = bytearray([0] * (3 * settings.LEDS_TOTAL))
        userdata.presenter_out = SerialInterface()
        userdata.interpreter_out = Eyes()
        userdata.current_mode_out = "eyes"
        for i in range(len(self.neuron_data)):
            self.neuron_data[i] = 0

        domecontrol().loop(self.neuron_data)

        while not settings.CHANGE_REQUESTED: #wait for incoming message
            pass
        return "transition"

class transition(smach.State): #gjerne endre slik at denne kun velger type,og settes i neste state
    def __init__(self):
        smach.State.__init__(self,outcomes=["meafromserver","meafromfile","nonmea"],
                                  input_keys=["next_mode_in"],
                                  output_keys=["next_mode_out","current_mode_out"])

    def execute(self,userdata):
        #global _next_mode,_current_mode,_interpreter
        rospy.loginfo("led_dome state change requested")
        settings.CHANGE_REQUESTED = False

        #for startup, before _next_mode is set
        """  if userdata.next_mode_in is not None:
            print("next_mode in transition: %s"%userdata.next_mode_in)
            userdata.current_mode_out = userdata.next_mode_in
            print("current_mode in transition: %s"%_current_mode)
            userdata.next_mode_out = None """
        userdata.current_mode_out = userdata.next_mode_in
        userdata.next_mode_out = None

        if userdata.current_mode_out == "siren" or "eyes":
            """if _current_mode == "siren":
                _interpreter = Siren()
                print("Interpreter changed to Siren")
            elif _current_mode == "eyes":
                _interpreter = Eyes()
                print("Interpreter changed to eyes")"""
            return "nonmea"
            
        else:
            """if _current_mode == "random":
                _interpreter = RandomMode()
            elif _current_mode == "moving-average":
                _interpreter = MovingAverage()
            elif _current_mode == "intensity":
                _interpreter = Intensity()"""    
            return "meafromfile"
           


class meafromserver(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=["transition"])

    def execute(self,userdata):
       """  rospy.loginfo("")
        global _source
        _source.loop() """
        #return "transition"

        
class meafromfile(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=["transition"])

    def execute(self,userdata): 
        """ rospy.loginfo("")
        global _source,_presenter
        _source = FileServer(loop,_presenter) """
        return "transition"

class nonmea(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=["transition"],
                                input_keys=["current_mode_in"],
                                output_keys=["interpreter_out"])
        self.neuron_data = [0] * settings.NEURAL_ELECTRODES_TOTAL
        settings.CHANGE_REQUESTED = False
        #setup rest of environment here

    def execute(self,userdata):
        rospy.loginfo("executing nonmea")

        print("nonmea mode: %s"% userdata.current_mode_in) #info about mode 
        for i in range(len(self.neuron_data)):
            self.neuron_data[i] = 0
        if userdata.current_mode_in == "siren":
            userdata.interpreter_out = Siren()
        elif userdata.current_mode_in == "eyes":
            userdata.interpreter_out = Eyes()
        else:
            #error handling?
            pass
        #check if interpreter is static or needs looping
        if userdata.interpreter_in.isStatic: 
            domecontrol().loop(self.neuron_data)
            while not settings.CHANGE_REQUESTED:
                pass
        else:
            while not settings.CHANGE_REQUESTED:
                domecontrol().loop(self.neuron_data)
        return "transition"

def domecontrol():

    #global _source, _interpreter,_led_colors,_presenter,_next_mode,_current_mode
    #_led_colors = bytearray([0] * (3 * settings.LEDS_TOTAL))
    #_presenter = SerialInterface()
    #_current_mode = "eyes"
    sm = smach.StateMachine(outcomes=[]) #do i need to fill
    sm.userdata.sm_source = None
    sm.userdata.sm_presenter=SerialInterface()
    sm.userdata.sm_interpreter = None
    sm.userdata.sm_led_colors = None
    sm.userdata.sm_current_mode = None
    sm.userdata.sm_next_mode = None
    rospy.Subscriber("dome_control", String, callback,sm.userdata.sm_next_mode)

    def loop(self,data):
        self.sm_interpreter.render(data, self.sm_led_colors)
        self.sm_presenter.refresh(self.sm_led_colors)

    

    with sm:
        smach.StateMachine.add("Startup",startup(),
               transitions={"transition":"Transition"},
                remapping={"presenter_out":"sm_presenter",
                           "interpreter_out":"sm_interpreter",
                           "led_colors_out":"sm_led_colors",
                           "current_mode_out":"sm_current_mode"})
        
        smach.StateMachine.add("Transition",transition(),
                transitions={"nonmea":"Nonmea","meafromfile":"MEAFromFile","meafromserver":"MEAFromServer"},
                remapping={"curent_mode_out":"sm_current_mode",
                           "next_mode_in":"sm_next_mode",
                           "next_mode_out":"sm_next_mode"})
        #smach.StateMachine.add("Idle",idle(),
         #                       transitions={"transition":"Transition"})
        smach.StateMachine.add("Nonmea",nonmea(),
                transitions={"transition":"Transition"},
                remapping={"current_mode_in":"sm_current_mode","interpreter_out":"sm_interpreter"})

        smach.StateMachine.add("MEAFromFile",meafromfile(),
                transitions={"transition":"Transition"})

        smach.StateMachine.add("MEAFromServer",meafromserver(),
                transitions={"transition":"Transition"})

    outcome = sm.execute()

if __name__=="__domecontrol__":
    domecontrol()






