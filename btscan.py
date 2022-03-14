import time
import pexpect
import subprocess
import json
import logging
from external_functions import *

class event_object():
    def __init__(self, event_json):
        
        self.event_name = event_json["Event Name"]
        
        # Determine how to compare against the RSSI value
        event_rssi_comparison = event_json["RSSI Comparison Type"]
        
        if(event_rssi_comparison == ">"):
            self.comparison_function = self.GreaterThanComparison
        elif(event_rssi_comparison == ">="):
            self.comparison_function = self.GreaterThanOrEqualComparison
        elif(event_rssi_comparison == "="):
            self.comparison_function = self.EqualComparison
        elif(event_rssi_comparison == "<"):
            self.comparison_function = self.LessThanComparison
        elif(event_rssi_comparison == "<="):
            self.comparison_function = self.LessThanOrEqualComparison
        elif(event_rssi_comparison == "Range"):
            self.comparison_function = self.RangeComparison
        else:
            logging.warn("Comparison type is invalid")
            self.comparison_function = None
        logging.debug(f"Comparison type {self.comparison_function}")

        self.event_rssi_threshold = event_json["RSSI Threshold"]
        logging.debug(f"RSSI threshold: {self.event_rssi_threshold}")

        self.dependent_events = dict()
        self.ParseConditions(event_json["Enabled By"], True)
        self.ParseConditions(event_json["Disabled By"], False)
        
        logging.debug(f"Dependent Events: {self.dependent_events}")
        
        # trigger_function = function_lookup.get(event_json["Function To Call When Triggered"])
        trigger_function = eval(event_json["Function To Call When Triggered"])
        if(trigger_function != None):
            self.event_trigger_function = trigger_function
        else:
            logging.warn(f"""Trigger Function does not exist for {event_json["Function To Call When Triggered"]}""")

        self.last_time_event_was_triggered = 0
        self.time_between_events = event_json["Time Interval Before Next Event Can Trigger"] # wait 3 seconds after each even occurs to trigger another event

    def ParseConditions(self, event_conditions, condition_value):

        for event_name in event_conditions:
            if(event_name == "Default"):
                self.trigger_enabled = condition_value
                logging.debug(f"Event {self.event_name} is {self.trigger_enabled} by default")
            elif(event_name == "Self"):
                logging.debug(f"Event {self.event_name} is Turned off by itself")
                self.dependent_events[self.event_name] = condition_value
            else:
                self.dependent_events[event_name] = condition_value
            
    def GreaterThanComparison(self, rssi):
        return rssi > self.event_rssi_threshold

    def GreaterThanOrEqualComparison(self, rssi):
        return rssi >= self.event_rssi_threshold

    def EqualComparison(self, rssi):
        return rssi == self.event_rssi_threshold

    def LessThanComparison(self, rssi):
        return rssi < self.event_rssi_threshold

    def LessThanOrEqualComparison(self, rssi):
        return rssi <= self.event_rssi_threshold

    def RangeComparison(self, rssi):
        return self.event_rssi_threshold[0] <= rssi <= self.event_rssi_threshold[1]
            
    def ExecuteTrigger(self):
        if((time.time() - self.last_time_event_was_triggered) > self.time_between_events):
            logging.debug("TRIGGERING EVENT")
            # Trigger the event by calling in the passed in function name
            self.event_trigger_function()
            # Set the time the event was triggered so we don't trigger again until a certain time has passed
            self.SetTriggerTime()
            self.SetDependentEventTriggerTimes()
            self.TriggerDependentFunctions()
        
    def SetTriggerTime(self):
        self.last_time_event_was_triggered = time.time()

    def SetDependentEventTriggerTimes(self):
        for (event_object, enabled_or_disabled) in self.dependent_events.values():
            event_object.last_time_event_was_triggered = self.last_time_event_was_triggered
    
    def CheckRSSIThreshold(self, rssi):
        if(self.comparison_function(rssi)):
            self.ExecuteTrigger()
            
    def TriggerDependentFunctions(self):
        for (event_object, enabled_or_disabled) in self.dependent_events.values():
            event_object.trigger_enabled = enabled_or_disabled
            logging.debug(f"Event {event_object.event_name} is now set to {enabled_or_disabled}")

class trigger_events():
    def __init__(self):
        self.event_dict = dict()

    def addEvent(self, event_object):
        self.event_dict[event_object.event_name] = event_object

    def CheckRSSIThreshold(self, rssi):
        for single_event_object in self.event_dict.values():
            # logging.debug(f"{single_event_object.event_name} is {single_event_object.trigger_enabled}")
            if(single_event_object.trigger_enabled == True):
                # RSSI values are negative so the lower (less negative) a value is the closer it is to the sensor
                single_event_object.CheckRSSIThreshold(rssi)

    def ResolveEventDependencies(self):
        for single_event_object in self.event_dict.values():
            for (dependent_event, enabled_or_disabled) in single_event_object.dependent_events.items():
                single_event_object.dependent_events[dependent_event] = (self.event_dict.get(dependent_event), enabled_or_disabled)

def run(command, seconds_to_run_for):
    time_end = time.time() + seconds_to_run_for
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    while time.time() < time_end:
        line = process.stdout.readline().rstrip()
        if not line:
            break
        yield line

if __name__ == "__main__":
    # INFO = LOWEST, DEBUG = HIGHEST
    logging.basicConfig(level=logging.INFO)

    triggering_events = trigger_events()
    with open("trigger_event_list.json", "r") as event_file:
        event_attributes = json.load(event_file)
        BLUETOOTH_MAC_WHITELIST = event_attributes["Bluetooth MAC Addresses"]
        for event in event_attributes["Events"]:
            logging.debug(event)
            single_event = event_object(event)
            triggering_events.addEvent(single_event)
    
    triggering_events.ResolveEventDependencies()

    btctl = pexpect.spawn("bluetoothctl", echo=False, encoding='utf-8')
    
    btctl.sendline("menu scan")
    btctl.sendline("duplicate-data on")
    btctl.sendline("back")
    btctl.sendline("scan on")

    complete_string = ""
    mac_address = ""
    for line in run("btmon", 10):
        str_line = str(line)
        if("Address: " in str_line):
            split_line = str_line.split("Address: ")
            address = split_line[1].split(" ")
            complete_string = f"Address: {address[0]}, "
            mac_address = str(address[0])
        elif("RSSI: " in str_line):
            split_line = str_line.split("RSSI: ")
            rssi = split_line[1].split(" ")
            complete_string = complete_string + f"RSSI: {rssi[0]}"
            print(complete_string)
            complete_string = ""
            
            # Check if the mac address is in the whitelist
            if(mac_address not in BLUETOOTH_MAC_WHITELIST):
                triggering_events.CheckRSSIThreshold(int(rssi[0]))


    btctl.sendline("scan off")
    time.sleep(0.5)
    btctl.sendline("exit")
    btctl.expect(pexpect.EOF, timeout=1)
    btctl.close(force=True)