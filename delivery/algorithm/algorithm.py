from abc import ABC, abstractmethod
import math
import random
from timeit import default_timer as timer
import copy
import itertools

from delivery.simulation.model.transportation import Delivery
from delivery.simulation.simulation import Simulation


def single_score(turns_taken, total_turns):
    if turns_taken >= total_turns:
        return 0

    return math.ceil((total_turns - turns_taken)/total_turns * 100)


class Algorithm(ABC):

    def __init__(self, simulation, max_time=None, max_iterations=None, max_improveless_iterations=20):
        self.simulation = simulation

        self.starting_time = timer()
        self.iterations = 0
        self.improveless_iterations = 0

        self.max_time = max_time
        self.max_iterations = max_iterations
        self.max_improveless_iterations = max_improveless_iterations

    @abstractmethod
    def run(self):
        pass

    def random_solution(self):
        simulation = copy.deepcopy(self.simulation)

        simulation.orders.sort(
            key=lambda order: self.simulation.order_weight(order.id))

        solution = []

        for order in simulation.orders:
            for product_type in order.product_types:
                warehouse, product = simulation.closest_warehouse(
                    order.location, product_type)

                drone = simulation.random_drone()

                transportation = simulation.assign_transportation(
                    warehouse, drone, product, order)

                solution.append(transportation)

        random.shuffle(solution)
        return solution

    def evaluate(self, solution):
        # TODO
        deliveries = self.split_into_deliveries(solution)

        score = 0
        # copies the orders to not complete the original ones
        delivered_orders = copy.deepcopy(self.simulation.orders)

        for drone in deliveries:
            # the starting location of the drone
            location = self.simulation.warehouses[0].location
            total_turns = 0

            # completes all the deliveries of the drone
            for delivery in drone:
                # realizes a deliver, updating the drone location and number of turns taken
                turns, location = self.simulation.deliver(delivery, location)
                total_turns += turns

                # if the total number of turns is exceeded, doesn't count anymore
                if total_turns >= self.simulation.environment.turns:
                    break

                # updates the order of that delivery if it applies
                Simulation.update_order(
                    delivered_orders, delivery, total_turns)

        for order in delivered_orders:
            if order.is_complete():
                score += single_score(order.turns,
                                      self.simulation.environment.turns)

        if score == 0:
            score = 1

        return score

    def split_into_deliveries(self, solution):
        # splits the solution into solutions for single drones
        drone_count = self.simulation.environment.drones_count
        drone_jobs = [[] for _ in range(drone_count)]

        for transportation in solution:
            drone_jobs[transportation.drone].append(transportation)

        # builds deliveries for the drones
        # ie joining of transportation
        deliveries = []
        for job in drone_jobs:
            deliveries.append(Delivery.build_deliveries(
                job, self.simulation.environment.drone_max_payload))

        return deliveries

    def stop(self):
        """Verifies if the algorithm must stop.

        ...
        Returns:
            boolean: True if the algorithm must stop, false otherwise
        """
        return self.max_time is not None and timer() - self.starting_time >= self.max_time \
            or self.max_iterations is not None and self.iterations >= self.max_iterations \
            or self.max_improveless_iterations <= self.improveless_iterations