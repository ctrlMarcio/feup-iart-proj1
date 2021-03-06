from delivery.simulation.model.order import Order
from delivery.output.command import Command


class Transportation:

    def __init__(self, product, drone, source, destination):
        """Instantiates a transportation

        ...
        Args:
            product (Product): The product to be moved
            drone (integer): The drone assigned to the product
            source (Warehouse): The place where the product comes from
            destination (Place): The place to be delivered
        """

        self.product = product
        self.drone = drone
        self.source = source
        self.destination = destination

    def is_final(self):
        return isinstance(self.destination, Order)

    def hash_source(self):
        return hash((self.product.id, self.source.id))

    def hash_destination(self):
        return hash((self.product.id, self.destination.id))

    def __str__(self):
        identifier = 'o' if isinstance(self.destination, Order) else 'w'
        return f'p{self.product.id} d{self.drone} w{self.source.id} {identifier}{self.destination.id}'

    def __repr__(self):
        return self.__str__()


class Delivery:
    """Treats the delivery of a set of products to a destination.

    Much like Transportation (a gene of the algorithm), but with a number of products that can be more than one. Drones
    do not deliver the products one by one, the products have to be grouped when they are sent to the same destination
    by the same drone, this class represents one of this delivers.
    """

    def __init__(self, products, drone, source, destination):
        self.products = products
        self.drone = drone
        self.source = source
        self.destination = destination

        self.__update_weight()
        self.__update_product_types()

    @classmethod
    def build_deliveries(cls, drone_transportation, payload):
        """Builds deliveries grouping the transportation of a drone.

        The transportation that are assigned to the same destination and are next to each other are grouped into a single
        delivery, as long as the drone payload is not exceeded. 

        ...
        Args:
            drone_transportation (list[Transportation]): The list of transportation that are assigned to a drone. It is
                                                         assumed that all this transportation are already assigned to
                                                         the same drone
            payload (integer): The maximum capacity of a drone

        Returns:
            list[Delivery]: The built list of delivers
        """
        res = []  # the returning list
        last_delivery = None  # the delivery that is being built in real time

        for transportation in drone_transportation:
            if last_delivery is None or last_delivery.source != transportation.source or last_delivery.destination != transportation.destination or last_delivery.weight + transportation.product.weight > payload:
                # if not the same as last delivery, just builds a new delivery and puts it in the res
                last_delivery = cls([transportation.product],
                                    transportation.drone, transportation.source, transportation.destination)
                res.append(last_delivery)
            else:
                # if the transportation is for the same delivery and the payload allows it, just adds the new product
                last_delivery.add(transportation.product)

        return res

    @classmethod
    def build_commands(cls, drone_transportation, payload):
        commands = []  # the returning list
        last_delivery = None  # the delivery that is being built in real time

        for transportation in drone_transportation:
            if last_delivery is None or last_delivery.source != transportation.source or last_delivery.destination != transportation.destination or last_delivery.weight + transportation.product.weight > payload:
                # if not the same as last delivery, just builds a new delivery and puts it in the res
                if last_delivery is not None:
                    commands.extend(last_delivery.to_commands())

                last_delivery = cls([transportation.product],
                                    transportation.drone, transportation.source, transportation.destination)
            else:
                # if the transportation is for the same delivery and the payload allows it, just adds the new product
                last_delivery.add(transportation.product)

        if last_delivery is not None:
            commands.extend(last_delivery.to_commands())

        return commands

    @property
    def weight(self):
        return self.__weight

    @property
    def product_types(self):
        return self.__product_types

    def add(self, product):
        """Adds a product to the tranpostation.

        ...
        Args:
            product (Product): The product to add
        """
        self.products.append(product)
        self.__weight += product.weight

    def is_final(self):
        return isinstance(self.destination, Order)

    def to_commands(self):
        product_count = {}

        for product in self.products:
            if product.type in product_count:
                product_count[product.type] += 1
            else:
                product_count[product.type] = 1

        load_commands = []
        deliver_commands = []

        for type, count in product_count.items():
            load_commands.append(
                Command(self.drone, 'L', self.source.id, type, count))
            deliver_commands.append(
                Command(self.drone, 'D', customer_id=self.destination.id, product_type=type, number_of_items=count))

        return load_commands + deliver_commands

    def __update_weight(self):
        self.__weight = 0
        for product in self.products:
            self.__weight += product.weight

    def __update_product_types(self):
        # creates a list without repeated products
        # products are repeated if they are from the same type
        types = []
        [types.append(x) for x in self.products if x not in types]

        # the number of product types is the size of the create list
        self.__product_types = len(types)

    def __str__(self):
        identifier = 'o' if isinstance(self.destination, Order) else 'w'
        product_types = [product.type for product in self.products]
        return f'p{product_types} d{self.drone} w{self.source.id} {identifier}{self.destination.id}'

    def __repr__(self):
        return self.__str__()
