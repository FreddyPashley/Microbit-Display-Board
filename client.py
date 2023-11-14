from microbit import *
import machine
import radio
import time


class Client:
    def __init__(self):
        self.serial = self.getSerial()
        self.radio = {
            "channel": 0,
            "length": 250
        }
        radio.config(**self.radio)


    def getSerial(self):
        return hex(machine.mem32[268435556] & 4294967295)
    

    def display(self, character:str):
        display.show(character)

    
    def clear(self):
        display.clear()

    def image(self, image_name:str):
        image = getattr(Image, image_name)
        display.show(image)
    

CLIENT = Client()

while True:
    message = radio.receive()