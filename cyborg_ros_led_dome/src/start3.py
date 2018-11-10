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
from neural_interpreter.individual_moving_average import IndividualMovingAverage
from neural_sources.file.file_server import FileServer
from neural_sources.server.client import Client
from neural_interpreter.snake import Snake

    
class startup(smach.State):
    def __init__(self, loopfunction):
        smach.State.__init__(self,outcomes=["transition"],
                               output_keys=["presenter_out","interpreter_out",
                                            "led_colors_out","current_mode_out"])
        self.loop = loopfunction
    def execute(self,userdata):
        neuron_data = [0] * settings.NEURAL_ELECTRODES_TOTAL
        settings.CHANGE_REQUESTED = False
        userdata.led_colors_out = bytearray([0] * (3 * settings.LEDS_TOTAL))
        userdata.presenter_out = SerialInterface()
        userdata.interpreter_out = Eyes()
        userdata.current_mode_out = "eyes" 
        #redundant?
        """for i in range(len(neuron_data)):
            neuron_data[i] = 0"""
        self.loop(neuron_data)
        self.loop(neuron_data)
       
        #wait for incoming message
        while not settings.CHANGE_REQUESTED and not rospy.is_shutdown(): 
            pass
        return "transition"

class transition(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=["meafromserver","meafromfile","nonmea"],
                                input_keys=["next_mode_in","current_mode_in","led_colors",],
                               output_keys=["next_mode_out","current_mode_out",
                                            "led_colors", "interpreter_out"]) 
    def execute(self,userdata):
        #byttet fra under userdata.next_mode
        settings.CHANGE_REQUESTED = False
        #maybe redundant:
        userdata.led_colors = bytearray([0]*(3*settings.LEDS_TOTAL))
        rospy.loginfo("led_dome state change requested")
        print("%s mode requested"%userdata.next_mode_in)        
        userdata.current_mode_out = userdata.next_mode_in
        print("userdata.current_mode set to:%s"%userdata.current_mode_in)
        userdata.next_mode_out = None
        
        if userdata.current_mode_in in ("siren","eyes","random-mode","snake"):
            print("nonmea-current.mode after transition, before return:%s"%userdata.current_mode_in)
            print("nonmea-next.mode after transition, before return:%s"%userdata.next_mode_in)
            return "nonmea"

        else:
            print("file-current.mode after transition, before return:%s"%userdata.current_mode_in)
            print("file-next.mode after transition, before return:%s"%userdata.next_mode_in)
            return "meafromfile"


#currently not implemented, included for completeness
class meafromserver(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=["transition"])

    def execute(self,userdata):
       """  rospy.loginfo("")
        global _source
        _source.loop() """
        #return "transition"

        
class meafromfile(smach.State):
    def __init__(self, loopfunction, return_interpreter):
        smach.State.__init__(self,outcomes=["transition"],
                                input_keys=["current_mode_in","presenter","interpreter"],
                               output_keys=["interpreter","presenter"])
        self.return_interpreter = return_interpreter
        self.loop = loopfunction
    def execute(self,userdata): 
        rospy.loginfo("executing meafromfile, mode: %s"%userdata.current_mode_in)
        userdata.presenter.reset()
        userdata.interpreter = self.return_interpreter(userdata.current_mode_in)
        source= FileServer(self.loop,SerialInterface)
        #source = Client(loop,SerialInterface)

        rate = rospy.Rate(10)
        rate.sleep()   
        source.loop()
        return "transition"



class nonmea(smach.State):
    def __init__(self, loopfunction, return_interpreter):
        smach.State.__init__(self,outcomes=["transition"],
                                input_keys=["current_mode_in","interpreter_in","presenter"],
                               output_keys=["interpreter_out","presenter"])
        self.neuron_data = [0] * settings.NEURAL_ELECTRODES_TOTAL
        self.return_interpreter = return_interpreter
        self.loop = loopfunction

    def execute(self,userdata):
        rospy.loginfo("executing nonmea")
        #may be redundant with esp32
        userdata.presenter.reset()
        print("nonmea mode: %s"% userdata.current_mode_in) 
        userdata.interpreter_out=self.return_interpreter(userdata.current_mode_in)
        #need delay for correct output 
        #may be redundant with esp32
        rate = rospy.Rate(10)
        rate.sleep()    

        if userdata.interpreter_in.isStatic:
            self.loop(self.neuron_data) 
            while not settings.CHANGE_REQUESTED and not rospy.is_shutdown():
                pass
        else:
            while not settings.CHANGE_REQUESTED and not rospy.is_shutdown():
                self.loop(self.neuron_data)
                
        return "transition"

    
def domecontrol():
    
    sm = smach.StateMachine(outcomes=[])
    sm.userdata.sm_source = None  
    sm.userdata.sm_presenter=SerialInterface()
    sm.userdata.sm_interpreter = None
    sm.userdata.sm_led_colors = None
    sm.userdata.sm_current_mode = None
    sm.userdata.sm_next_mode = None

    def loop(data):
        sm.userdata.sm_interpreter.render(data,sm.userdata.sm_led_colors)
        sm.userdata.sm_presenter.refresh(sm.userdata.sm_led_colors)

    def return_interpreter(mode):
        print("returning %s"% mode)
        if "moving-average" in mode:
            return MovingAverage()
        elif "intensity" in mode:
            return Intensity()
        elif "individual-moving-average" in (mode):
            return IndividualMovingAverage()
        elif "random-mode" in mode:
            return RandomMode()
        elif "siren" in mode:
            return Siren()
        elif "eyes" in mode:
            return Eyes()
        elif "snake" in mode:
            return Snake()
        else:
            #error handling?
            pass

    def callback(data):
        if sm.userdata.sm_current_mode != data.data:
            settings.CHANGE_REQUESTED = True
            print("previous mode: %s"%sm.userdata.sm_current_mode)
            sm.userdata.sm_next_mode = data.data
            print("requested mode: %s"%sm.userdata.sm_next_mode)

    rospy.Subscriber("dome_control", String, callback)

    with sm:
        smach.StateMachine.add("Startup",startup(loop),
               transitions={"transition":"Transition"},
                 remapping={"presenter_out":"sm_presenter",
                            "interpreter_out":"sm_interpreter",
                            "led_colors_out":"sm_led_colors",
                            "current_mode_out":"sm_current_mode"})
        
        smach.StateMachine.add("Transition",transition(),
                transitions={"nonmea":"Nonmea",
                             "meafromfile":"MEAFromFile",
                             "meafromserver":"MEAFromServer"},
                  remapping={"current_mode_in":"sm_current_mode",
                             "current_mode_out":"sm_current_mode",
                             "next_mode_in":"sm_next_mode",
                             "next_mode_out":"sm_next_mode",
                             "led_colors":"sm_led_colors",
                             "interpreter_out":"sm_interpreter"})

        smach.StateMachine.add("Nonmea",nonmea(loop,return_interpreter),
                transitions={"transition":"Transition"},
                  remapping={"current_mode_in":"sm_current_mode",
                             "interpreter_in":"sm_interpreter",
                             "interpreter_out":"sm_interpreter",
                             "presenter":"sm_presenter"})

        smach.StateMachine.add("MEAFromFile",meafromfile(loop,return_interpreter),
                transitions={"transition":"Transition"},
                  remapping={"current_mode_in":"sm_current_mode",
                             "current_mode_out":"sm_current_mode",
                             "presenter":"sm_presenter",
                             "interpreter":"sm_interpreter"})

        smach.StateMachine.add("MEAFromServer",meafromserver(),
                transitions={"transition":"Transition"})

    outcome = sm.execute()

if __name__=="__domecontrol__":
    domecontrol()






