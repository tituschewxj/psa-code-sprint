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
        self.schedule = PriorityQueue(key=lambda x: x[0])

        # Populate pq with data from arr
        for [time, cargo_unload_amount, cargo_load_amount] in arr:
            self.schedule.put([time, cargo_unload_amount, cargo_load_amount])


    # Return next ship time & cargo amount
    def get_next_ship(self):
        return self.schedule.dequeue()
        

    @staticmethod
    def check_ship_schedules(self):
        return self.schedule 
    