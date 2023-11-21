VERSION = "v0.4"

from microbit import *
import radio
import machine
import random


class Client:
    
    def __init__(self, radio_config:dict):
        self.version = VERSION
        radio.config(**radio_config)
        radio.off()
        self.serial = str(self.calculate_serial_number())
        self.location = None

    def calculate_serial_number(self):
        return hex(machine.mem32[268435556] & 4294967295)
    
    def send(self, text:str, msg_id:int=None):
        msg_id = random.randint(3, 10000) if msg_id is None else msg_id
        # Format text with locations here
        to_send = ["SERVER", str(msg_id), 0, text]
        radio.send(":".join([str(i) for i in to_send]))
    

# Main
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
                    display.show(data)
                elif status_code == 2:  # Pre-set instruction
                    if data == "clear":
                        display.clear()
                    elif data == "serial":
                        display.scroll(client.serial)
                    elif data.startswith("id-mode"):
                        while True:
                            display.scroll("ID")
                            if button_a.was_pressed():
                                client.send(str(client.serial), msg_id=msg_id)
                                break
                            if button_b.was_pressed():
                                client.send(str(client.serial)+"-", msg_id=msg_id)
                                break
                        display.show(Image.YES)
                    elif data.startswith("self-loc"):
                        coordinates = data.strip("self-loc,").split(",")
                        row, bot_in_row = [int(i) for i in coordinates]
                        client.location = {"row": row, "bot_in_row": bot_in_row}
                    else:
                        display.show(Image.ANGRY)  # Instruction is confusing... 