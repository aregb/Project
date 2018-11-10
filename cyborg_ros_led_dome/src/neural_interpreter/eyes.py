#!/usr/bin/env python
import rospy
import system.settings as settings



class Eyes():

    def __init__(self):
        self.isStatic = True
    def render(self,input_data, output_data):
        print("rendering eyes")
        for i in range(settings.LEDS_TOTAL):
            output_data[i*3 ] = 0
            output_data[i*3 + 1] = 0
            output_data[i*3 + 2] = 0

            #right eye
        """output_data[444*3+2] = 55
        output_data[445*3+2] = 55
        output_data[446*3+2] = 55
        output_data[478*3+2] = 55
        output_data[479*3+2] = 55
        output_data[480*3+2] = 55
        output_data[481*3+2] = 55
        output_data[482*3+2] = 55
        output_data[509*3+2] = 55
        output_data[510*3+2] = 55
        output_data[511*3+2] = 55

        #left eye
        output_data[453*3+2] = 55
        output_data[454*3+2] = 55
        output_data[455*3+2] = 55
        output_data[487*3+2] = 55
        output_data[488*3+2] = 55
        output_data[489*3+2] = 55
        output_data[490*3+2] = 55
        output_data[491*3+2] = 55
        output_data[518*3+2] = 55
        output_data[519*3+2] = 55
        output_data[520*3+2] = 55 """
        for i in range(20):
            output_data[i*3+1] = 100

        #print(output_data[0])
        #print(output_data[3+1])
        #print(output_data[6+1])
        #print(output_data[9+1])
        #print(output_data[12+1])


         
        #output_data[50]=100
        #output_data[600]=60


