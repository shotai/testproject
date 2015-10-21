class stack:
    def __init__(self):
        self.name = ""
        self.services = []

    def add_service(self, name):
        self.services.append(name)
