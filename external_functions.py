
from phue import Bridge

ifttt_websocket_url = "https://maker.ifttt.com/trigger/:event/json/with/key/hjcwUc4ehMp9UiBpYJtEzzVUzHInxcNTEmc21ClEcKb"
turn_off_bedroom_light_event = "turn_off_bedroom_light_event"
reading_hour_activated_event = "reading_hour_activated_event"
blue_hour_activated_event = "blue_hour_activated_event"

def TestFunctionOn():
        print("Called Test Function On")

def TestFunctionOff():
        print("Called Test Function Off")

def TurnOnBedroomLights():
        b = Bridge('192.168.1.112')

        # If the app is not registered and the button is not pressed, press the button and call connect() (this only needs to be run a single time)
        b.connect()

        # Get the bridge state (This returns the full dictionary that you can explore)
        b.get_api()

        # Prints if light 1 is on or not
        print(f"Bedroom is currently on: {b.get_light(1, 'on')}")

        # Set brightness of lamp 2 to 50%
        b.set_light(2, 'bri', 127)

        # You can also control multiple lamps by sending a list as lamp_id
        b.set_light( [1,2], 'on', True)

        # Prints if light 1 is on or not
        print(f"Bedroom is currently on: {b.get_light(1, 'on')}")

        print("Turned on Bedroom lights")

def TurnOffBedroomLights():
        b = Bridge('192.168.1.112')

        # If the app is not registered and the button is not pressed, press the button and call connect() (this only needs to be run a single time)
        b.connect()

        # Get the bridge state (This returns the full dictionary that you can explore)
        b.get_api()

        # Prints if light 1 is on or not
        print(f"Bedroom is currently on: {b.get_light(1, 'on')}")

        # You can also control multiple lamps by sending a list as lamp_id
        b.set_light( [1,2], 'on', False)

        # Prints if light 1 is on or not
        print(f"Bedroom is currently on: {b.get_light(1, 'on')}")

        print("Turned off Bedroom lights")

def TurnOnLivingRoomLights():
        print("Turned on Living Room lights")

def TurnOffLivingRoomLights():
        print("Turned off Living Room lights")

def ArmLivingRoomCamera():
        print("Arming Living Room Camera")
        event = "blink_armed_event"
        response = requests.get(ifttt_websocket_url.replace(":event", event))
        if response.status_code == 200:
                print("Living Room Camera Armed Successfully.")
        else:
                print("Arming Living Camera Failed.")

def DisarmLivingRoomCamera():
        print("Disarming Living Room Camera")
        event = "blink_disarmed_event"
        response = requests.get(ifttt_websocket_url.replace(":event", event))
        if response.status_code == 200:
                print("Living Room Camera Disarmed Successfully.")
        else:
                print("Disarming Living Camera Failed.")

def TurnOnReadingLight():
        print("Turning Reading Light On")
        response = requests.get(ifttt_websocket_url.replace(":event", reading_hour_activated_event))
        if response.status_code == 200:
                print("Reading Light Turned On Successfully.")
        else:
                print("Turning Reading Light On Failed.")

def TurnOnBlueLight():
        print("Turning Blue Light On")
        response = requests.get(ifttt_websocket_url.replace(":event", blue_hour_activated_event))
        if response.status_code == 200:
                print("Blue Light Turned On Successfully.")
        else:
                print("Turning Blue Light On Failed.")

def TurnOffAllLight():
        print("Turning All Light Off")
        response = requests.get(ifttt_websocket_url.replace(":event", turn_off_bedroom_light_event))
        if response.status_code == 200:
                print("All Light Turned Off Successfully.")
        else:
                print("Turning All Light Off Failed.")

