class Stack:
    def __init__(self):
        self.name = ""
        self.services = []

    def print_stack(self):
        print("STACK: " + self.name + " SERVICES: " + " ".join(self.services))

