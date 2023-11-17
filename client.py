VERSION = "v0.1"

from microbit import *
import radio
import machine


class Client:
    
    def __init__(self, radio_config:dict):
        self.version = VERSION
        radio.config(**radio_config)
        radio.off()
        self.serial = str(self.calculate_serial_number())

    def calculate_serial_number(self):
        return hex(machine.mem32[268435556] & 4294967295)
    

# Main
client = Client(radio_config={"channel": 0, "length": 250})
radio.on()

while True:
    message = radio.receive()
    if message:  # Has a message been detected?
        message_data = message.split(":")
        if len(message_data) == 4:  # Is the received transmission useful to us?
            recipient, msg_id, status_code, data = message_data
            if recipient == client.serial:  # Is the received transmission for us?
                msg_id = int(msg_id)
                status_code = int(status_code)
                if status_code == 3:  # Display data
                    display.show(data)
                elif status_code == 2:  # Pre-set instruction
                    if data == "clear":
                        display.clear()
                    elif data == "serial":
                        data.scroll(client.serial)
                    elif data == "id-mode":
                        pass  # To be implemented
                    else:
                        display.show(Image.ANGRY)  # Instruction is confusing... 