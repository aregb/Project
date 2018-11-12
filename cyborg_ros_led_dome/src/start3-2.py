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
    def __init__(self, loopfunction,update_visualization_mode):
        smach.State.__init__(self,outcomes=["nonmea","meafromfile"],
                               output_keys=["presenter_out","interpreter_out",
                                            "led_colors_out","current_interpreter_out"])
        self.loop = loopfunction
        self.update_visualization_mode = update_visualization_mode

    def execute(self,userdata):
        neuron_data = [0] * settings.NEURAL_ELECTRODES_TOTAL
        userdata.led_colors_out = bytearray([0] * (3 * settings.LEDS_TOTAL))
        userdata.presenter_out = SerialInterface()
        userdata.interpreter_out = Eyes()
        userdata.current_interpreter_out = "eyes" 
        self.loop(neuron_data)
       
        #wait for incoming message
        while not settings.CHANGE_REQUESTED and not rospy.is_shutdown(): 
            pass

        return self.update_visualization_mode()


#currently not implemented, included for completeness
class meafromserver(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=["nonmea"])

    def execute(self,userdata):
       """  rospy.loginfo("")
        global _source
        _source.loop() """
        #return "transition"

        
class meafromfile(smach.State):
    def __init__(self, loopfunction, return_interpreter,update_visualization_mode):
        smach.State.__init__(self,outcomes=["nonmea","meafromfile"],
                                input_keys=["current_interpreter_in","presenter","interpreter"],
                               output_keys=["interpreter","presenter"])
        self.return_interpreter = return_interpreter
        self.loop = loopfunction
        self.update_visualization_mode = update_visualization_mode
    def execute(self,userdata): 
        rospy.loginfo("executing meafromfile, interpreter: %s"%userdata.current_interpreter_in)
        userdata.presenter.reset()
        userdata.interpreter = self.return_interpreter(userdata.current_interpreter_in)
        source= FileServer(self.loop,SerialInterface)

        rate = rospy.Rate(10)
        rate.sleep()   
        source.loop()
        return self.update_visualization_mode()



class nonmea(smach.State):
    def __init__(self, loopfunction, return_interpreter,update_visualization_mode):
        smach.State.__init__(self,outcomes=["nonmea","meafromfile"],
                                input_keys=["current_interpreter_in","interpreter_in","presenter"],
                               output_keys=["interpreter_out","presenter"])
        self.neuron_data = [0] * settings.NEURAL_ELECTRODES_TOTAL
        self.return_interpreter = return_interpreter
        self.loop = loopfunction
        self.update_visualization_mode = update_visualization_mode

    def execute(self,userdata):
        rospy.loginfo("executing nonmea")
        #may be redundant with esp32
        userdata.presenter.reset()
        userdata.interpreter_out=self.return_interpreter(userdata.current_interpreter_in)
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
                
        return self.update_visualization_mode()
    
def domecontrol():
    #make init and write function as class instead
    #make difference mode and iterpreter
    sm = smach.StateMachine(outcomes=[])
    sm.userdata.sm_source = None  # fjerne
    sm.userdata.sm_presenter=SerialInterface() #fjerne
    sm.userdata.sm_interpreter = None #fjerne
    sm.userdata.sm_led_colors = None #fjerne
    sm.userdata.sm_mode = None
    sm.userdata.sm_current_interpreter = None
    sm.userdata.sm_next_interpreter = None


    def loop(data):
        sm.userdata.sm_interpreter.render(data,sm.userdata.sm_led_colors)
        sm.userdata.sm_presenter.refresh(sm.userdata.sm_led_colors)

    def return_interpreter(interpreter):
        if "moving-average" in interpreter:
            return MovingAverage()
        elif "intensity" in interpreter:
            return Intensity()
        elif "individual-moving-average" in interpreter:
            return IndividualMovingAverage()
        elif "random-mode" in interpreter:
            return RandomMode()
        elif "siren" in interpreter:
            return Siren()
        elif "eyes" in interpreter:
            return Eyes()
        elif "snake" in interpreter:
            return Snake()
        else:
            #error handling?
            pass

    def update_visualization_mode():
        rospy.loginfo("led_dome state change requested")
        settings.CHANGE_REQUESTED = False       
        sm.userdata.sm_current_interpreter = sm.userdata.sm_next_interpreter
        sm.userdata.sm_next_interpreter_out = None

        if sm.userdata.sm_current_interpreter in ("siren","eyes","random-mode","snake"):
            sm.userdata.sm_mode = "nonmea"
            return sm.userdata.sm_mode
        else:
            sm.userdata.sm_mode = "meafromfile"
            return sm.userdata.sm_mode
        
    def callback(data):
        if sm.userdata.sm_current_interpreter != data.data:
            settings.CHANGE_REQUESTED = True
            sm.userdata.sm_next_interpreter = data.data

    rospy.Subscriber("dome_control", String, callback)


    #initiate state machine
    with sm:
        smach.StateMachine.add("Startup",startup(loop,update_visualization_mode),
               transitions={"nonmea":"Nonmea",
                            "meafromfile":"MEAFromFile"},
                 remapping={"presenter_out":"sm_presenter",
                            "interpreter_out":"sm_interpreter",
                            "led_colors_out":"sm_led_colors",
                            "current_interpreter_out":"sm_current_interpreter"})
        
        smach.StateMachine.add("Nonmea",nonmea(loop,return_interpreter,update_visualization_mode),
                transitions={"nonmea":"Nonmea",
                             "meafromfile":"MEAFromFile"},
                  remapping={"current_interpreter_in":"sm_current_interpreter",
                             "interpreter_in":"sm_interpreter",
                             "interpreter_out":"sm_interpreter",
                             "presenter":"sm_presenter"})

        smach.StateMachine.add("MEAFromFile",meafromfile(loop,return_interpreter,update_visualization_mode),
                transitions={"nonmea":"Nonmea",
                             "meafromfile":"MEAFromFile"},
                  remapping={"current_interpreter_in":"sm_current_interpreter",
                             "presenter":"sm_presenter",
                             "interpreter":"sm_interpreter"})

        smach.StateMachine.add("MEAFromServer",meafromserver(),
                transitions={"nonmea":"Nonmea"})
                
    #execute state machine
    outcome = sm.execute()

if __name__=="__domecontrol__":
    domecontrol()






