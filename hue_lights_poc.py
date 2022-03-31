from phue import Bridge
import struct
import sys

import bluetooth
import bluetooth._bluetooth as bluez  # low level bluetooth wrappers

from btscan.proximitydetection  import FilterAddExpiration, FilterSetProximity
from btscan.btscanner           import FileBTMonitor, BTMonitor, FilterAddLocation, SCANNER_PATH
from btscan.namelookup          import FilterNameLookup, FileBTNameDriver

from btscan.constants           import *

def SetLights():
    b = Bridge('192.168.1.112')

    # If the app is not registered and the button is not pressed, press the button and call connect() (this only needs to be run a single time)
    b.connect()

    # Get the bridge state (This returns the full dictionary that you can explore)
    b.get_api()

    # Prints if light 1 is on or not
    print(b.get_light(1, 'on'))


proximity_filter= FilterSetProximity( SetLights, {})