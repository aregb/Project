#!/usr/bin/env python
import rospy
import system.settings as settings



class Siren():
    def __init__(self):
        self.previous_color = "blue"
<<<<<<< HEAD
        self.rate = rospy.Rate(16)
=======
        self.rate = rospy.Rate(2)
>>>>>>> 0becafcf638e3305c445a5f527c516d9a8ded909
        self.isStatic = False #looping needed


    def render(self, input_data, output_data):
        print("rendering siren")
        if settings.CHANGE_REQUESTED:
            pass
        else:
            if self.previous_color == "blue":
                for i in range(settings.LEDS_TOTAL):
                    output_data[i*3 ] = 10
                    output_data[i*3 + 1] = 0
                    output_data[i*3+ 2] = 0
                self.previous_color = "red"
            else:
                for i in range(settings.LEDS_TOTAL):
                    output_data[i*3 ] = 0
                    output_data[i*3 + 1] = 0
                    output_data[i*3 + 2] = 10
                self.previous_color = "blue"
            self.rate.sleep()
