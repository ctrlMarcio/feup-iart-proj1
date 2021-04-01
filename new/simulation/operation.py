from model.place import Client

class Operation:
    def __init__(self, item, destination, drone):
        self.item = item
        self.destination = destination
        self.drone = drone

    def copy(self):
        return Operation(self.item, self.destination, self.drone)

    def is_final(self):
        return isinstance(self.destination, Client)

    def __str__(self):
        def normalize(string, n):
            string = str(string)
            return " " * (n - len(string)) + string
        drone = normalize(self.drone, 4)
        item = normalize(self.item, 15)
        destination = normalize(self.destination, 17)
        return drone + " moves " + item + " to " + destination
