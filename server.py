DATA = "Hi [duck]"  # Edited by user to trigger display
BOTS = [1, 1]  # Edited if necessary to change number of expected bots (rows, bots_per_row)
"""
Valid instructions:
clear - 'Turns off' the display
serial - All bots display their serial number for manual identification
(image_name) - An image existing in the microbit library
"""

VERSION = "v0.5"
INSTRUCTIONS = ["clear", "serial"]

from microbit import *
import radio
import machine
import random


class Server:
    
    def __init__(self, radio_config:dict):
        self.version = VERSION
        radio.config(**radio_config)
        radio.off()
        self.serial = str(self.calculate_serial_number())
        self.bots = [
            ["0x237e64e7", "0xbb1e263", "0x4f020d8b", "0x67cf561a"]
        ]  # Add serials

    def calculate_serial_number(self):
        return hex(machine.mem32[268435556] & 4294967295)
    
    def instruct(self, recipient:str="ALL", instruction:str="clear"):
        msg_id = random.randint(1, 10000)
        to_send = [recipient, str(msg_id), 2, instruction]
        radio.send(":".join([str(i) for i in to_send]))

    def display(self, recipient:str="ALL", text:str="TEST"):
        msg_id = random.randint(1, 10000)
        text_list = []
        image_name = ""
        detecting_image = False
        for character in text:
            if character == "[":
                detecting_image = True
            elif character == "]":
                detecting_image = False
                text_list.append(image_name)
                image_name = ""
            elif detecting_image:
                image_name += character
            else:
                text_list.append(character)
        row = 0
        for counter, character in enumerate(text_list):
            if counter == 20:
                counter = 0
                row += 1
                if row == 3: break
            recipient = self.bots[row][counter]
            to_send = [recipient, str(msg_id), 3, character]
            radio.send(":".join([str(i) for i in to_send]))


# Main
server = Server(radio_config={"channel": 0, "length": 250})
radio.on()

if DATA != "":
    if DATA in INSTRUCTIONS:
        server.instruct(instruction=DATA)
    else:
        server.display(text=DATA)

while True:
    message = radio.receive()
    if message:  # Has a message been detected?
        message_data = message.split(":")
        if len(message_data) == 4:  # Is the received transmission useful to us?
            recipient, msg_id, status_code, data = message_data
            if recipient == "SERVER":  # Is the received transmission for us?
                msg_id = int(msg_id)
                status_code = int(status_code)
                # Do stuff with transmission