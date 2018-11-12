#!/usr/bin/env python
"""Created by Areg Babayan on 20/9/2018.
Copyright (C) 2018 Areg Babayan. ALl rights reserved."""
__author__      = "Areg Babayan"
__copyright__   = "Copyright (C) 2018 Areg Babayan"
__license__     = "BSD"
__version__     = "0.0.3"
__all__         = []   # why this?

import rospy
import start3


def main():
    rospy.init_node("cyborg_led_dome")
    start3.domecontrol()




if __name__ == '__main__':
    print("Cyborg LED Dome: Starting Program...")
    main()
    print("Cyborg LED Dome: End of Program...")