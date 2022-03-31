
from phue import Bridge


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
