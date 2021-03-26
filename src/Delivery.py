from Place import *
from Path import *
from random import randrange
from math import ceil


class Data:
    def __init__(self, rows, columns, drones, turns, payload, weights):
        self.numberOfRows = int(rows)
        self.numberOfColumns = int(columns)
        self.numberOfDrones = int(drones)
        self.numberOfTurns = int(turns)
        self.maxPayload = int(payload)
        self.productWeights = tuple(map(int, weights))

    def evaluateSolution(self, solution):
        turns = self.numberOfDrones * [self.numberOfTurns]
        score = 0
        factor = 1 / self.numberOfTurns * 100
        for path in solution:
            # TODO: Take into account the time a drone needs to go to the next warehouse before delivering it
            turns[path.drone] -= path.duration()
            if turns[path.drone] < 0:
                continue
            score += ceil(turns[path.drone] * factor)
        return score


class Delivery:
    def __init__(self, rows, columns, drones, turns, payload, weights, warehouses, clients):
        self.data = Data(rows, columns, drones, turns, payload, weights)
        self.warehouses = warehouses
        self.clients = clients
        self.products = [
            product for warehouse in warehouses for product in warehouse.products
        ]
        self.solution = self.initialSolution()

    def initialSolution(self):
        def assignProducts():
            productsNotAssigned = self.products
            ordersSortedBySize = sorted(self.clients, key=len)
            for order in ordersSortedBySize:
                print(len(productsNotAssigned))
                #productsNotAssigned = sorted(
                #    productsNotAssigned, key=order.distanceToProduct
                #)
                for productType in order.wantedProducts:
                    i = 0
                    for product in productsNotAssigned:
                        if product.productType == productType:
                            break
                        i += 1
                    productsNotAssigned.pop(i).assignOrder(order)

        def assignDrones(solution):
            for path in solution:
                path.assignDrone(randrange(self.data.numberOfDrones))

        assignProducts()
        solution = list(
            map(Path, filter(lambda x: x.hasOrder(), self.products)))
        assignDrones(solution)
        return sorted(solution, key=lambda x: x.drone)

    def toOutputFile(self, file):
        with open("data/" + file + ".out", "w+") as outputFile:
            outputFile.write(str(2 * len(self.solution)) + "\n")
            for path in self.solution:
                outputFile.write(path.getOutputString())

    def evaluateSolution(self):
        return self.data.evaluateSolution(self.solution)

    @classmethod
    def fromInputFile(cls, file):
        with open("data/" + file + ".in") as inputFile:
            # Problem
            problemInformation = inputFile.readline().split()
            numberOfProducts = inputFile.readline()
            productWeights = inputFile.readline().split()

            # Warehouses
            numberOfWarehouses = int(inputFile.readline())
            warehouses = []
            for i in range(numberOfWarehouses):
                warehouseCoordinates = inputFile.readline().split()
                warehouseItems = inputFile.readline().split()
                newWarehouse = Warehouse(
                    i, warehouseCoordinates, warehouseItems)
                warehouses.append(newWarehouse)

            # Orders
            numberOfOrders = int(inputFile.readline())
            clients = []
            for i in range(numberOfOrders):
                orderCoordinates = inputFile.readline().split()
                orderNumberOfItems = inputFile.readline()
                orderProducts = inputFile.readline().split()
                newClient = Client(i, orderCoordinates, orderProducts)
                clients.append(newClient)

            return Delivery(*problemInformation, productWeights, warehouses, clients)
