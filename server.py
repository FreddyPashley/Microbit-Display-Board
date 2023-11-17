DATA = ""  # Edited by user to trigger display
INSTRUCTION = True  # True/False for display vs instruction
"""
Valid instructions:
clear - 'Turns off' the display
serial - All bots display their serial number for manual identification
id-mode - System for remembering where bots are for future use
"""

VERSION = "v0.2"

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
        self.bots = []

    def calculate_serial_number(self):
        return hex(machine.mem32[268435556] & 4294967295)
    
    def instruct(self, instruction:str):
        msg_id = random.randint(1, 10000)
        radio.send(f"ALL:{msg_id}:2:{instruction}")

    def display(self, text:str):
        msg_id = random.randint(1, 10000)
        # Format text with locations here
        radio.send(f"ALL:{msg_id}:3:{text}")  # Change recipients from ALL to specific serials after id-mode implementation


# Main
server = Server(radio_config={"channel": 0, "length": 250})
radio.on()

if DATA != "":
    if DATA == "id-mode":
        pass  # To be implemented later
    else:
        if INSTRUCTION:
            server.instruct(DATA)
        else:
            server.display(DATA)

while True:
    message = radio.receive()
    if message:  # Has a message been detected?
        message_data = message.split(":")
        if len(message_data) == 4:  # Is the received transmission useful to us?
            recipient, msg_id, status_code, data = message_data
            if recipient == "SERVER":  # Is the received transmission for us?
                msg_id = int(msg_id)
                status_code = int(status_code)
                # Do what you need to with responses later