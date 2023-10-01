import mesa
import networkx as nx
import numpy as np
import pandas as pd
import schedules

"""
Agent based modelling to simulate a port.
"""
from constants import MAX_SHIPS_AT_BERTH
from schedules import ShipSchedules

class ShipAgent(mesa.Agent):
    def __init__(self, unique_id, model, agent_store, cargo_unload_amount: int, cargo_load_amount: int, max_cargo_capacity: int):
        super(unique_id, model)
        self.agent_store: AgentStore = agent_store
        self.cargo_unload_amount = cargo_unload_amount
        self.cargo_load_amount =  cargo_load_amount
        self.max_cargo_capacity = max_cargo_capacity
        self.is_at_berth = False
        self.is_loading_cargo = False
        self.is_unloading_cargo = False

    def unload_cargo(self):
        self.cargo_amount -= 1

    def load_cargo(self):
        self.cargo_amount += 1
        return

    def arrive_at_berth(self):
        self.is_at_berth = True

    
    def depart_from_berth(self):
        self.is_at_berth = False

    def step(self):
        if (self.is_at_berth):
            # can unload cargo or load cargo. this is determined by the state of the ship, whether it is unloading
            if (self.is_loading_cargo):
                self.load_cargo()
            
            if (self.is_unloading_cargo):
                self.unload_cargo()
        else:
            # check ship schedule information if new ship should arrive
            # can only arrive if berth is not full (=> measure inefficiencies)




            return

# class BerthAgent(mesa.Agent):
#     """Represents a berth where ships arrive. In our simulation, there is only one berth"""
#     def __init__(self, unique_id, model, agent_store):
#         super(unique_id, model)
#         self.agent_store: AgentStore = agent_store
#         self.ships = set()

#     def receive_ship(self, ship_agent: ShipAgent):
#         self.ships.add(ship_agent)
        
#     def depart_ship(self, ship_agent: ShipAgent):
#         self.ships.remove(ship_agent)

#     def step(self):
        
#         ship_agents = self.agent_store.get_ship_agents()
#         agv_agents = self.agent_store.get_agv_agents()
        
#         # Check the status of ships and update ship's is_at_birth if fully unloaded
#         for ship in ship_agents:
#             if ship.is_at_birth:
#                 ship.depart_from_birth()
                
class AGVAgent(mesa.Agent):
    """Cargo transport vehicle agent"""
    def __init__(self, unique_id, model, agent_store):
        super(unique_id, model)
        self.agent_store: AgentStore = agent_store
        self.is_active = False
        return
    
    def step(self):
        crane_agents = self.agent_store.get_crane_agents()
        storage_agents = self.agent_store.get_storage_agents()
        charing_point_agents = self.agent_store.get_charging_point_agents()
    
class CraneAgent(mesa.Agent):
    """Crane that carries one cargo, this crane moves cargo from ship to agv."""
    def __init__(self, unique_id, model, agent_store):
        super(unique_id, model)
        self.agent_store: AgentStore = agent_store
        self.is_active = False
        self.average_rate_load = 100
        self.average_rate_unload = 100
        
        # remaining_cargo is estimated/computed
        self.remaining_cargo = 100

    def step(self):
        storage_agents = self.agent_store.get_storage_agents()
        charing_point_agents = self.agent_store.get_charging_point_agents()
    
class StorageAgent(mesa.Agent):
    def __init__(self, unique_id, model, agent_store):
        super(unique_id, model)
        self.agent_store: AgentStore = agent_store
        self.current_capacity = 0
        self.max_capacity = 100

    def step(self):
        return

class ChargingPointAgent(mesa.Agent):
    def __init__(self, unique_id, model, agent_store):
        super(unique_id, model)
        self.agent_store: AgentStore = agent_store
        self.powerSupplied = 100
        self.is_charging_something = False

class AgentStore():
    """AgentStore represents the different agents"""
    def __init__(self):
        # create empty sets
        self.ship_agents = set()
        self.berth_agents = set()
        self.agv_agents = set()
        self.crane_agents = set()
        self.charging_point_agents = set()
        self.storage_agents = set()

    def add_ship_agent(self, ship_agent: ShipAgent):-
        self.ship_agents.add(ship_agent)

    # def add_berth_agent(self, berth_agent: BerthAgent):
    #     self.ship_agents.add(berth_agent)

    def add_agv_agent(self, agv_agent: AGVAgent):
        self.ship_agents.add(agv_agent)

    def add_crane_agent(self, crane_agent: CraneAgent):
        self.ship_agents.add(crane_agent)

    def add_storage_agent(self, storage_agent: StorageAgent):
        self.ship_agents.add(storage_agent)

    def add_charging_point_agent(self, charging_point_agent: ChargingPointAgent):
        self.ship_agents.add(charging_point_agent)

    def get_ship_agents(self):
        return self.ship_agents

    def get_berth_agents(self):
        return self.berth_agents

    def get_agv_agents(self):
        return self.agv_agents

    def get_crane_agents(self):
        return self.crane_agents

    def get_storage_agents(self):
        return self.storage_agents

    def get_charging_point_agents(self):
        return self.charging_point_agents
    

class PortModel(mesa.Model):
    """A model to represent the port."""

    """
    Ship/agv/crane agents: max number of ships/agv/crane that the port can support.
    """
    # Takes in as parameter a ShipSchedules object (with populated pq) 
    def __init__(self, ship_agents: int, agv_agents: int, crane_agents: int, ship_schedule: ShipSchedules):
        self.berth_agents = 1
        self.storage_agents = 1
        self.ship_agents = ship_agents
        self.agv_agents = agv_agents
        self.crane_agents = crane_agents
        self.agent_store = AgentStore()
        self.schedule = mesa.time.RandomActivation(self)
        
        # Create ShipAgents
        self.agent_count = 0
        for _ in range(self.ship_agents):

            # Get next ship via dequeue
            next_ship = ship_schedule.get_next_ship()

            # Create next ShipAgent
            a = ShipAgent(self.agent_count, self, self.agent_store, next_ship[1], next_ship[2])
            self.agent_store.add_ship_agent(a)
            self.agent_count += 1

        #Create BerthAgents
        # self.berth_count = 0
        # for _ in range(self.berth_agents):
        #     a = BerthAgent(self.berth_count, self, self.agent_store)
        #     self.agent_store.add_berth_agent(a)
        #     self.berth_count += 1

        #Create StorageAgents
        self.storage_count = 0
        for _ in range(self.storage_agents):
            a = StorageAgent(self.storage_count, self, self.agent_store)
            self.agent_store.add_storage_agent(a)
            self.storage_count += 1

        #Create agvAgents
        self.agv_count = 0
        for _ in range(self.agv_agents):
            a = AGVAgent(self.agv_count, self, self.agent_store)
            self.agent_store.add_agv_agent(a)
            self.agv_count += 1

        #Create CraneAgents
        self.crane_count = 0
        for _ in range(self.crane_agents):
            a = CraneAgent(self.crane_count, self, self.agent_store)
            self.agent_store.add_crane_agent(a)
            self.crane_count += 1
   
        return

    def step(self):
        """Advance the model by one step."""
        self.schedule.step()
