
class Node():
    def __init__(self, name):
        self.name = name
        self.iface = ""

class Switch():
    def __init__(self, name):
        self.name = name
        self.iface = ""

class Link():
    def __init__(self, device1, device2):
        self.conPoint_1 = device1
        self.conPoint_2 = device2