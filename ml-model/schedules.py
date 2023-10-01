from queue import PriorityQueue
import numpy as np


class ShipSchedules():
    """
    Encapsulates the arrivals and departures of ships.
    Uses a forecast of ship arrival times to simulate the ship arrivals.
    
    Allow the user to schdule some ships initially.
    """
    #Implement queue for the arrival times
    # 2 cols - Arrival Time, Cargo amount, 
    #Assume data is in numpy array
    #If berth full, dequeue will be delayed, can track the delay duration in test_model perhaps
    

    """
    Takes in an np.array, that has the discrete ship arrivals: Their arrival time and cargo amount. 
    """
    def __init__(self, arr) -> None:

        # Order pq based on smallest date value
        self.delayed_ships = []
        self.scheduled_ships = PriorityQueue(10000)
        # Populate pq with data from arr
        for [cargo_load_amount, time] in arr:
            self.scheduled_ships.put((time, (cargo_load_amount, cargo_load_amount)))
        
        # set the initial time
        self.set_time()


    # Returns a tuple of cargo data, or none if operation fails
    def try_get_next_ship(self):
        if len(self.delayed_ships) > 0:
            return self.delayed_ships.pop(0)
        
        return None

    def force_get_next_ship(self):
        data = self.try_get_next_ship()
        if data != None:
            return data
        
        self.set_time()
        return self.scheduled_ships.get()

        
    def set_time(self):
        data = self.peek_into_scheduled_ships()
        if data == None:
            return
        
        self.time = data[0]

    def peek_into_scheduled_ships(self):
        if self.scheduled_ships.empty():
           return None
        
        temp = self.scheduled_ships.get()
        self.scheduled_ships.put(temp)
        return temp

    # has ship waiting in schedule 
    def has_ship_waiting(self)-> bool:
        if not(self.scheduled_ships.empty()):
            data = self.peek_into_scheduled_ships()
            if data != None:
                return data[0] < self.time
        
        return False

    def get_delayed_ship_count(self):
        return len(self.delayed_ships)
    
    def step(self):
        self.time = self.time + 1000

        while self.has_ship_waiting():
            self.delayed_ships.append(self.scheduled_ships.get())
        
    