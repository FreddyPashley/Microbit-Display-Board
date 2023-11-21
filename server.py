DATA = "serial"  # Edited by user to trigger display
BOTS = 1  # Edited if necessary to change number of expected bots
"""
Valid instructions:
clear - 'Turns off' the display
serial - All bots display their serial number for manual identification
id-mode - System for remembering where bots are for future use
"""

VERSION = "v0.4"
INSTRUCTIONS = ["clear", "serial", "id-mode"]

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
        self.bots = [[]]

    def calculate_serial_number(self):
        return hex(machine.mem32[268435556] & 4294967295)
    
    def instruct(self, recipient:str="ALL", instruction:str="clear"):
        if instruction == "id-mode":
            msg_id = 1
        elif instruction.startswith("self-loc"):
            msg_id = 2
        elif instruction.startswith("gather-loc"):
            msg_id = 3
        else:
            msg_id = random.randint(4, 10000)
        to_send = [recipient, str(msg_id), 2, instruction]
        radio.send(":".join([str(i) for i in to_send]))

    def display(self, recipient:str="ALL", text:str="TEST"):
        msg_id = random.randint(3, 10000)
        # Format text with locations here
        to_send = [recipient, str(msg_id), 3, text]
        radio.send(":".join([str(i) for i in to_send]))


# Main
server = Server(radio_config={"channel": 0, "length": 250})
radio.on()

if DATA != "":
    if DATA == "id-mode":
        server.instruct(instruction="id-mode")
    else:
        if server.bots == [[]]:
            server.bots = {}
            server.instruct(instruction="gather-loc")
            while True:
                if len(server.bots) == BOTS: break
                message = radio.receive()
                if message:
                    message_data = message.split(":")
                    if len(message_data) == 4:  # Is the received transmission useful to us?
                        recipient, msg_id, status_code, data = message_data
                        if recipient == "SERVER":  # Is the received transmission for us?
                            msg_id = int(msg_id)
                            status_code = int(status_code)
                            if msg_id == 3:
                                serial, coordinates = data.split(",")[0], data.split(",")[1:]
                                row, bot_in_row = [int(i) for i in coordinates]
                                letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                                server.bots[letters[row]+str(bot_in_row)] = serial
            bots_in_rows = {k:len([i for i in server.bots.keys() if i.startswith(k)]) for k in letters if k in [i[0] for i in server.bots.keys()]}
            final_bots = []
            for k in bots_in_rows:
                final_bots.append([0 for i in range(bots_in_rows[k])])
            for coordinate in server.bots:
                row = letters.index(coordinate[0])
                if len(coordinate) > 2:
                    bot_in_row = int(coordinate[1:])
                else:
                    bot_in_row = int(coordinate[0])
                final_bots[row][bot_in_row] = server.bots[coordinate]
            server.bots = final_bots
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
                if msg_id == 1:
                    rows = len(server.bots)
                    bots = 0
                    for i in range(rows):
                        bots += len(server.bots[i])
                    if bots != BOTS:
                        server.bots[-1].append(data.strip("-"))
                        if data.endswith("-"):
                            server.bots.append([])
                    else:
                        for i, row in enumerate(server.bots):
                            for j, bot_serial in enumerate(row):
                                coordinates = ",".join([i, j])
                                server.instruct(recipient=str(bot_serial), instruction="self-id,"+coordinates)