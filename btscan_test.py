import time
import pexpect
import subprocess
import json

BLUETOOTH_MAC_WHITELIST = ["D8:0B:9A:CB:DA:CF", "57:99:9E:33:5A:8B", "5C:01:ED:92:1B:0A"]



def TurnOnBedroomLights():
        print("Turned on Bedroom lights")

def TurnOffBedroomLights():
        print("Turned off Bedroom lights")

def TurnOnLivingRoomLights():
        print("Turned on Living Room lights")

def TurnOffLivingRoomLights():
        print("Turned off Living Room lights")

function_lookup = {
    "TurnOnBedroomLights":TurnOnBedroomLights,
    "TurnOffBedroomLights":TurnOffBedroomLights,
    "TurnOnLivingRoomLights":TurnOnLivingRoomLights,
    "TurnOffLivingRoomLights":TurnOffLivingRoomLights,
}

class event_object():
    def __init__(self, event_json):
        
        self.event_name = event_json["Event Name"]
        
        # Determine how to compare against the RSSI value
        event_rssi_comparison = event_json["RSSI Comparison Type"].lower()
        
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
            print("Comparison type is invalid")
            self.comparison_function = None
        print(f"Comparison type {self.comparison_function}")

        # Determine if a single value or a range
        print(eval(event_json["RSSI Threshold"]))
        if(eval(event_json["RSSI Threshold"])) == list):
            self.event_rssi_threshold = event_json["RSSI Threshold"]
        else:
            self.event_rssi_threshold = event_json["RSSI Threshold"]
        print(f"RSSI threshold: {self.event_rssi_threshold}")

        self.dependent_functions = dict()
        self.ParseConditions(event_json["Enabled By"])
        self.ParseConditions(event_json["Disabled By"])
        
        print(f"Dependent Functions: {self.dependent_functions}")

        trigger_function = function_lookup.get(event_trigger_function)
        self.event_trigger_function = trigger_function
        
        self.trigger_enabled = False
        self.dependent_events = dict()

    def ParseConditions(self, event_conditions):
        condition_type, conditions, after_conditions = event_conditions.split("\"")
        if(condition_type.lower() == "enabled by "):
            condition_value = True
        elif(condition_type.lower() == "disabled by "):
            condition_value = False
        else:
            print("Invalid condition type")

        event_names = conditions.split(",")
        for event_name in event_names:
            if(event_name == "Default"):
                print(f"Event {self.event_name} is {condition_value} by default")
                self.dependent_functions[self] = condition_value
                self.trigger_enabled = condition_value
            else:
                self.dependent_functions[event_name] = condition_value
            
    def GreaterThanComparison(self, rssi):
        if(rssi > self.event_rssi_threshold):
            # Trigger the event by calling in the passed in function name
            self.event_trigger_function()
            return True
        else:
            return False

    def GreaterThanOrEqualComparison(self, rssi):
        if(rssi >= self.event_rssi_threshold):
            # Trigger the event by calling in the passed in function name
            self.event_trigger_function()
            return True
        else:
            return False

    def EqualComparison(self, rssi):
        if(rssi == self.event_rssi_threshold):
            # Trigger the event by calling in the passed in function name
            self.event_trigger_function()
            return True
        else:
            return False


    def LessThanComparison(self, rssi):
        if(rssi < self.event_rssi_threshold):
            # Trigger the event by calling in the passed in function name
            self.event_trigger_function()
            return True
        else:
            return False

    def LessThanOrEqualComparison(self, rssi):
        if(rssi <= self.event_rssi_threshold):
            # Trigger the event by calling in the passed in function name
            self.event_trigger_function()
            return True
        else:
            return False

    def RangeComparison(self, rssi):
        if(self.event_rssi_threshold[0] <= rssi <= self.event_rssi_threshold[1]):
            # Trigger the event by calling in the passed in function name
            self.event_trigger_function()
            return True
        else:
            return False
    
    def CheckRSSIThreshold(self, rssi):
        if(self.comparison_function(rssi)):
            self.TriggerDependentFunctions

    def TriggerDependentFunctions(self):
        for (event_object, enabled_or_disabled) in self.dependent_functions:
            event_object.trigger_enabled = enabled_or_disabled

class trigger_events():
    def __init__(self):
        self.event_dict = dict()

    def addEvent(self, event_object):
        self.event_dict[event_object.event_name] = event_object

    def CheckRSSIThreshold(self, rssi):
        for single_event_object in self.event_dict.values():
            # RSSI values are negative so the lower (less negative) a value is the closer it is to the sensor
            single_event_object.CheckRSSIThreshold(rssi)

    def ResolveEventDependencies(self):
        for single_event in self.event_dict.values():
            for dependent_event, enabled_or_disabled in single_event.dependent_events.items():
                single_event.dependent_events[dependent_event] = (self.event_dict[dependent_event], enabled_or_disabled)


def run(command, seconds_to_run_for):
    time_end = time.time() + seconds_to_run_for
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    while time.time() < time_end:
        line = process.stdout.readline().rstrip()
        if not line:
            break
        yield line

if __name__ == "__main__":

    triggering_events = trigger_events()
    with open("trigger_event_list.txt", "r") as event_file:
        for event in json.load(event_file):

            print(event)
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
            if(mac_address in BLUETOOTH_MAC_WHITELIST):
                triggering_events.CheckRSSIThreshold(int(rssi[0]))


    btctl.sendline("scan off")
    time.sleep(0.5)
    btctl.sendline("exit")
    btctl.expect(pexpect.EOF, timeout=1)
    btctl.close(force=True)