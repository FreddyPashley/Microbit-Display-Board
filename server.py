DATA = ["Helloworld", "[happy][duck][happy][duck][happy][duck][happy][duck][happy][duck]"]
SWIPE_INTERVAL = 1.5  # Seconds for swipe to finish
SWIPE_SHOW = .1  # Seconds for each swipe block to move
"""
Valid instructions:
clear - 'Turns off' the display
serial - All bots display their serial number for manual identification
[image_name] - An image existing in the microbit library
"""

VERSION = "v0.7"
INSTRUCTIONS = ["clear", "serial"]

from microbit import *
import radio
import machine
import random
import time

class Server:
    
    def __init__(self, radio_config:dict):
        self.version = VERSION
        radio.config(**radio_config)
        radio.off()
        self.serial = str(self.calculate_serial_number())
        # self.bots = [
        #     ["0x7b9080a4", "0x6b9a492c", "0x5cbd7385", "0x3d85ecee", "0x5415f436", "0xec2990f2", "0xd85ab8c2", "0x5a10a2c0", "0x81deabbe", "0xb1d38abc", "0x7581dc19", "0xe7c04445", "0x85fb979d", "0x6901229e", "0xbf66ffb5", "0xf7e149c0", "0xa9d48785", "0x99904c2", "0x433cea7c", "0x58058793"],
        #     ["0x2c58cda", "0x2600e830", "0x177727a6", "0x7ad288b7", "0x964f8165", "0x1f96fdea", "0xab8b63ca", "0x9b645506", "0xb0005931", "0x2347e7f6"]
        # ]  # Add more serials...
        self.bots = [
            ["0x7b9080a4", "0x6b9a492c", "0x5cbd7385", "0x3d85ecee", "0x5415f436"],
            ["0xec2990f2", "0xd85ab8c2", "0x5a10a2c0", "0x81deabbe", "0xb1d38abc"]
        ]  # For prototype
        self.data_pos = 0

    def calculate_serial_number(self):
        return hex(machine.mem32[268435556] & 4294967295)
    
    def instruct(self, recipient:str="ALL", instruction:str="clear"):
        msg_id = random.randint(1, 10000)
        to_send = [recipient, str(msg_id), 2, instruction]
        radio.send(":".join([str(i) for i in to_send]))

    def display(self, recipient:str="ALL", text:list=["TEST"]):
        msg_id = random.randint(1, 10000)
        while True:
            text_list = []
            image_name = ""
            detecting_image = False
            for character in text[self.data_pos]:
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
            counter = -1
            for character in text_list:
                counter += 1
                if counter == len(self.bots[0]):
                    counter = 0
                    row += 1
                    if row == len(self.bots): break
                recipient = self.bots[row][counter]
                to_send = [recipient, str(msg_id), 3, character]
                radio.send(":".join([str(i) for i in to_send]))
            if len(text) == 1: break
            time.sleep(SWIPE_INTERVAL)
            rows = len(self.bots)
            bots_per_row = len(self.bots[0])
            brightness = {"9":[0, []],"6":[-1, []],"c":[-2, []]}
            while brightness["9"][0] < bots_per_row:
                brightness["9"][1] = []
                for i in range(rows):
                    brightness["9"][1].append([i, brightness["9"][0]])
                for bot_coord in brightness["9"][1]:
                    recipient = self.bots[bot_coord[0]][bot_coord[1]]
                    to_send = [recipient, str(msg_id), 3, "block-9"]
                    radio.send(":".join([str(i) for i in to_send]))
                if brightness["6"][0] >= 0:
                    brightness["6"][1] = []
                    for i in range(rows):
                        brightness["6"][1].append([i, brightness["6"][0]])
                    for bot_coord in brightness["6"][1]:
                        recipient = self.bots[bot_coord[0]][bot_coord[1]]
                        to_send = [recipient, str(msg_id), 3, "block-6"]
                        radio.send(":".join([str(i) for i in to_send]))
                if brightness["c"][0] >= 0:
                    brightness["c"][1] = []
                    for i in range(rows):
                        brightness["c"][1].append([i, brightness["c"][0]])
                    for bot_coord in brightness["c"][1]:
                        recipient = self.bots[bot_coord[0]][bot_coord[1]]
                        self.instruct(recipient=recipient)
                for k in brightness: brightness[k][0] += 1
                time.sleep(SWIPE_SHOW)
            self.instruct()
            if self.data_pos >= len(text)-1:
                self.data_pos = 0
            else:
                self.data_pos += 1


# Main
server = Server(radio_config={"channel": 0, "length": 250})
radio.on()

server.instruct()

if DATA != []:
    if DATA[0] in INSTRUCTIONS:
        server.instruct(instruction=DATA[0])
    else:
        server.display(text=DATA)
