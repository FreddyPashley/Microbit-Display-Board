from microbit import *
import radio
import machine
import random

VERSION = "v0.8"


class Client:

    def __init__(self, radio_config:dict):
        radio.config(**radio_config)
        radio.off()
        self.version = VERSION
        self.serial = str(self.calculate_serial_number())
        self.location = None

    def calculate_serial_number(self):
        return hex(machine.mem32[268435556] & 4294967295)
    

# Main program
client = Client(radio_config={"channel": 0, "length": 250})
radio.on()


while True:
    message = radio.receive()

    if message:  # Has a message been detected?
        message_data = message.split(":")

        if len(message_data) == 4:  # Is the received transmission useful to us?
            recipient, msg_id, status_code, data = message_data

            if recipient in [client.serial, "ALL"]:  # Is the received transmission for us?
                msg_id = int(msg_id)
                status_code = int(status_code)

                if status_code == 3:  # Display data
                    if data.startswith("block-"):
                        brightness = data.strip("block-")
                        display.show(Image(":".join([brightness*5 for i in range(5)])))
                    elif hasattr(Image, data.upper()):
                        display.show(getattr(Image, data.upper()))
                    else:
                        display.show(data)

                elif status_code == 2:  # Pre-set instruction
                    if data == "clear":
                        display.clear()
                    elif data == "serial":
                        display.scroll(client.serial)
                    else:
                        display.show(Image.ANGRY)  # Instruction is unknown and confusing... 