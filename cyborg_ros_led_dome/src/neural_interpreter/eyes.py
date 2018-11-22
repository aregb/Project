#!/usr/bin/env python
import rospy
import system.settings as settings



class Eyes():

    def __init__(self):
        self.isStatic = True
    def render(self,input_data, output_data):
            #right eye
        output_data[453*3+2] = 10
        output_data[454*3+2] = 55
        output_data[455*3+2] = 55
        output_data[456*3+2] = 10

        output_data[477*3+2] = 10
        output_data[478*3+2] = 55
        output_data[481*3+2] = 55
        output_data[482*3+2] = 10
        
        output_data[518*3+2] = 10
        output_data[519*3+2] = 55
        output_data[520*3+2] = 55
        output_data[521*3+2] = 10

        #left eye
        output_data[443*3+2] = 10
        output_data[444*3+2] = 55
        output_data[445*3+2] = 55
        output_data[446*3+2] = 10

        output_data[487*3+2] = 10
        output_data[488*3+2] = 55
        output_data[491*3+2] = 55
        output_data[492*3+2] = 10

        output_data[508*3+2] = 10
        output_data[509*3+2] = 55
        output_data[510*3+2] = 55
        output_data[511*3+2] = 10


