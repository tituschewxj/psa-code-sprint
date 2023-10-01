import mesa
from constants import MAX_SHIPS_AT_BERTH
import networkx as nx
import numpy as np
import pandas as pd
from constants import MAX_SHIPS_AT_BERTH
from schedules import ShipSchedules
import random

class ShipAgent(mesa.Agent):
    def __init__(self, unique_id, model, cargo_unload_amount: int, cargo_load_amount: int):
        super().__init__(unique_id, model)
        self.model: PortModel = model
        self.agent_store: AgentStore = self.model.agent_store

        self.cargo_current_amount = cargo_unload_amount
        self.cargo_load_amount =  cargo_load_amount

        # state - berth / unberth
        self.is_at_berth = False

        # state - load / unload
        self.is_unloading_cargo = True
        self.is_loading_cargo = False

        # state - complete / incomplete
        self.completed_tasks = False

    def try_unload_cargo(self) -> bool:
        print(self.cargo_current_amount)
        if (self.cargo_current_amount <= 0):
            # completed unloading. proceed to loading state
            self.is_unloading_cargo = False
            self.is_loading_cargo = True
            return False
        else:
            self.cargo_current_amount -= 1
            self.model.cargo_unloaded += 1
            return True

    def try_load_cargo(self) -> bool:
        if not(self.is_loading_cargo) or self.cargo_current_amount >= self.cargo_load_amount:
            return False
        if self.cargo_current_amount == self.cargo_load_amount - 1:
            # load final cargo. depart from berth after
            self.is_loading_cargo = False
            self.completed_tasks = True
            self.is_at_berth = False
            self.model.decrement_ships_at_berth()
        self.cargo_current_amount += 1
        self.model.cargo_loaded += 1
        return True

    # called by crane to load/unload
    def work_on_cargo(self) -> bool:
        self.model.crane_utilisation_count += 1

        if self.is_unloading_cargo:
            return self.try_unload_cargo()
        if self.is_loading_cargo:
            return self.try_load_cargo()
    
    def try_arrive_at_port(self):
        # check schedule.
        # TODO: fixup testing code
        data = self.model.ship_schedules.try_get_next_ship()
        # data = self.model.ship_schedules.force_get_next_ship()
        if data == None:
            return

        self.is_at_berth = True
        self.completed_tasks = False
        self.cargo_load_amount = data[1][0]
        self.cargo_current_amount = data[1][1]
        self.model.increment_ships_at_berth()

    def step(self):
        # Possible states: Completed tasks, Berthed, Unberthed & can't enter, Unberthed & can enter
        if (self.completed_tasks or self.is_at_berth):
            return

        if (self.model.get_ships_at_berth() < MAX_SHIPS_AT_BERTH):
            #Let ship arrive at berth
            self.try_arrive_at_port()


class CraneAgent(mesa.Agent):
    """Crane that carries one cargo, this crane moves cargo from ship to agv."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.model: PortModel = model
        self.agent_store: AgentStore = self.model.agent_store

        self.average_rate_load = 100
        self.average_rate_unload = 100
        self.is_carrying_cargo = False

        # is active: not under maintenance or charging
        self.is_active = False
        self.max_battery_level = 10
        self.battery_level = 10
        self.should_charge_battery = False

        self.working_on_ship: ShipAgent = None
        
    # A unit of energy is when performing a task
    # more energy may be used when performing tasks, which should be set by the user
    # based on how efficient the crane is.
    # Returns true if there is sufficient energy
    def use_energy(self) -> bool:
        self.battery_level = max(self.battery_level - 1, 0)
        if (self.battery_level == 0):
            # go to charging point
            self.model.out_of_battery_cranes += 1
            self.should_charge_battery = True
            return False
        
        return True

    # start working with a ship (unload/load cargo)
    def start_work(self, ship_agent):
        self.working_on_ship: ShipAgent = ship_agent

    # stop working with a ship
    def end_work(self):
        self.working_on_ship = None

    # called by agv to unload the agv
    def pass_to_agv(self):
        self.is_carrying_cargo = False

    def try_load_from_agv(self):
        if self.is_carrying_cargo:
            return False
        if self.working_on_ship.can_load_cargo_to_ship():
            self.is_carrying_cargo = True
            return True
        else:
            return False
             
    def step(self):
        ship_agents = self.agent_store.get_ship_agents()
        charing_point_agents = self.agent_store.get_charging_point_agents()

        self.use_energy()

        if self.should_charge_battery:
            # find charging point agent to charge.
            for charging_point in charing_point_agents:
                if charging_point.try_charge_something(self):
                    break
                else:
                    # Update inefficiency for delayed charging for CraneAgent
                    pass

        if self.working_on_ship == None:
            for ship in ship_agents:
                if ship.is_at_berth:
                    self.working_on_ship = ship
                    if self.working_on_ship.work_on_cargo():
                        self.is_carrying_cargo = not(self.is_carrying_cargo)
                    break
            return
               
        if self.is_carrying_cargo and self.working_on_ship.is_unloading_cargo:
            return

        if not(self.is_carrying_cargo) and self.working_on_ship.is_loading_cargo:
            return

        # otherwise keep working on the same ship
        if self.working_on_ship.work_on_cargo():
            self.is_carrying_cargo = not(self.is_carrying_cargo)


class AGVAgent(mesa.Agent):
    """Cargo transport vehicle agent"""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.model: PortModel = model
        self.agent_store: AgentStore = self.model.agent_store
        
        self.working_on_crane: CraneAgent = None
        self.is_transporting_cargo = False

        # check for crane -> storage / storage -> crane
        self.crane_to_storage = True
        
        # is active: not under maintenance or charging
        self.is_active = False
        self.battery_level = 10
        self.max_battery_level = 10
        self.should_charge_battery = False
      
    # def extract_from_storage(self, storage):
    #     return storage.try_extract_cargo() 

    def use_energy(self) -> bool:
        self.battery_level = max(self.battery_level - 1, 0)
        if (self.battery_level == 0):
            # go to charging point
            self.model.out_of_battery_agvs += 1
            self.should_charge_battery = True
            return False
        
        return True

    
    def step(self):
        crane_agents = self.agent_store.get_crane_agents()
        storage_agents = self.agent_store.get_storage_agents()
        charing_point_agents = self.agent_store.get_charging_point_agents()

        self.use_energy()


        if self.should_charge_battery:
            # find charging point agent to charge.
            for charging_point in charing_point_agents:
                if charging_point.try_charge_something(self):
                    self.model.out_of_battery_agvs += 1
                    self.model.power_usage += 1
                    break
            return

        # if agv is available
        if (~self.is_transporting_cargo):
            if self.working_on_crane == None:  
                n = random.randint(0, 1)
                if (n == 0):
                    # work for crane (crane -> storage)
                    for crane in crane_agents:
                        if not(crane.is_active):
                            continue
                        if crane.is_carrying_cargo:
                            crane.pass_to_agv()
                            self.working_on_crane = crane
                            self.is_transporting_cargo = True
                            self.crane_to_storage = True
                            self.model.agv_utilisation_count += 1
                            break
                else:
                    # work for storage (storage -> crane)
                    for storage in storage_agents:
                        if storage.try_extract_cargo():
                            self.is_transporting_cargo = True
                            self.working_on_crane = None
                            self.crane_to_storage = False
                            self.model.agv_utilisation_count += 1
                return    
            else:
                # continue working on current crane, if work available
                if self.working_on_crane.is_carrying_cargo and self.working_on_crane.is_active:
                    self.working_on_crane.pass_to_agv()
                    self.is_transporting_cargo = True
                    self.model.agv_utilisation_count += 1
                else:
                    # free the agv from crane
                    self.working_on_crane = None
                    self.crane_to_storage = True
                    self.step()
                return

        # if agv is carrying cargo
        if self.is_transporting_cargo:
            
            # if agv is bound for storage
            if self.crane_to_storage:
                # Find availble storage agents to store cargo. Record inefficiency if fail
                for storage in storage_agents:
                    if storage.try_store_cargo():
                        self.is_transporting_cargo = False
                        return
                self.model.delayed_agvs += 1
                return
            # if agv is bound for crane
            else:
                # Find available crane that is working on a ship with space to load. Record inefficiency if fail
                for crane in crane_agents:
                    if crane.try_load_from_agv():
                        self.is_transporting_cargo = False
                        return
                self.model.delayed_agvs += 1
                return


class StorageAgent(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.model: PortModel = model
        self.agent_store: AgentStore = self.model.agent_store
        self.current_capacity = 0
        self.max_capacity = 100
    
    def space_available(self):
        return self.current_capacity < self.max_capacity

    def try_store_cargo(self) -> bool:
        if (self.space_available):
            self.current_capacity += 1
            self.model.cargo_stored += 1
            return True
        
        return False

    def try_extract_cargo(self) -> bool:
        if self.current_capacity > 0:
            self.current_capacity -= 1
            self.model.cargo_retrieved += 1
            return True
        
        return False

    def step(self):
        # measure the space efficiency for that step
        self.model.cargo_volume_in_storage += self.current_capacity
        pass


class ChargingPointAgent(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.model: PortModel = model
        self.agent_store: self.model.agent_store
        
        self.powerSupplied = 1
        self.powerDraw = 0
        
        # refers to the object that it is charging.
        self.charging_something = None

    # Returns true if it is available: not charging something else
    def try_charge_something(self, object: AGVAgent | CraneAgent):
        if self.charging_something != None:
            return False

        # can charge
        self.charging_something = object
        object.is_active = False
        self.charge_something()
        return True

    # Call this when there is an object to charge
    def charge_something(self):
        if self.charging_something == None:
            self.powerDraw = 0
            return
         
        self.charging_something.battery_level += self.powerSupplied
        self.charging_something.battery_level = min(self.charging_something.max_battery_level, self.charging_something.battery_level)
        self.powerDraw = self.powerSupplied

        # update model statistics
        self.model.charging_point_utilisation_count += 1
        self.model.power_usage += self.powerDraw

    def step(self):
        self.charge_something()
        

class AgentStore():
    """AgentStore represents the different agents"""
    def __init__(self):
        # create empty sets
        self.ship_agents: set[ShipAgent] = set()
        self.agv_agents: set[AGVAgent] = set()
        self.crane_agents: set[CraneAgent] = set()
        self.charging_point_agents: set[ChargingPointAgent] = set()
        self.storage_agents: set[StorageAgent] = set()

    def add_ship_agent(self, ship_agent: ShipAgent):
        self.ship_agents.add(ship_agent)

    def add_agv_agent(self, agv_agent: AGVAgent):
        self.agv_agents.add(agv_agent)

    def add_crane_agent(self, crane_agent: CraneAgent):
        self.crane_agents.add(crane_agent)

    def add_storage_agent(self, storage_agent: StorageAgent):
        self.storage_agents.add(storage_agent)

    def add_charging_point_agent(self, charging_point_agent: ChargingPointAgent):
        self.charging_point_agents.add(charging_point_agent)

    def get_ship_agents(self):
        return self.ship_agents

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
        self.storage_agents = 1
        self.charging_point_agents = 50
        self.ship_agents = ship_agents
        self.agv_agents = agv_agents
        self.crane_agents = crane_agents
        
        # model data to collect (update and reset this sum at every step)
        self.ships_docked_at_port = 0
        self.reset_model_step_statistics()

        self.agent_store = AgentStore()
        self.ship_schedules = ship_schedule
        self.schedule = mesa.time.RandomActivation(self)
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "power_usage": lambda _: self.power_usage,
                "agv_utilisation_count": lambda _: self.agv_utilisation_count,
                "crane_utilisation_count": lambda _: self.crane_utilisation_count,
                "charging_point_utilisation_count": lambda _: self.charging_point_utilisation_count,
                "cargo_stored": lambda _: self.cargo_stored,
                "cargo_retrieved": lambda _: self.cargo_retrieved,
                "cargo_loaded": lambda _: self.cargo_loaded,
                "cargo_unloaded": lambda _: self.cargo_unloaded,
                "ships_docked_at_port": lambda _: self.ships_docked_at_port,
                "delayed_ships": lambda _: self.delayed_ships,
                "delayed_agvs": lambda _: self.delayed_agvs,
                "out_of_battery_cranes": lambda _: self.out_of_battery_cranes,
                "out_of_battery_agvs": lambda _: self.out_of_battery_agvs,
            },
            agent_reporters={
                "energy_usage": "energy_usage",
                "is_active": "is_active",
                "battery_level": "battery_level",
            },
        )
        
        # All agents need to have unique IDs, so that the collecting of agent-level variables work
        uid = 0

        # Create ShipAgents
        for _ in range(self.ship_agents):

            # FIXME: This implementation is wrong: the first step of the ABM will get the next ship instead, since at the start, the ships are inactive.
            # Better implementation would be to call step directly after init for ShipAgent 

            # Create & activate new ship agent
            next_ship = ship_schedule.force_get_next_ship()
            a = ShipAgent(uid, self, next_ship[0], next_ship[1])
            a.step() # Added activation of Ship Agents
            self.agent_store.add_ship_agent(a)
            uid += 1
            self.schedule.add(a)

        #Create StorageAgents
        for _ in range(self.storage_agents):
            a = StorageAgent(uid, self)
            self.agent_store.add_storage_agent(a)
            uid += 1
            self.schedule.add(a)

        #Create AGVAgents
        for _ in range(self.agv_agents):
            a = AGVAgent(uid, self)
            self.agent_store.add_agv_agent(a)
            uid += 1
            self.schedule.add(a)

        #Create CraneAgents
        for _ in range(self.crane_agents):
            a = CraneAgent(uid, self)
            self.agent_store.add_crane_agent(a)
            uid += 1
            self.schedule.add(a)

        #Create charging point
        for _ in range(self.charging_point_agents):
            a = ChargingPointAgent(uid, self)
            self.agent_store.add_charging_point_agent(a)
            uid += 1
            self.schedule.add(a)

    # reset or init model statistics that are collected per step.
    def reset_model_step_statistics(self):
        # Power usage statistics
        self.power_usage = 0
        
        # Utilisation statistics
        self.agv_utilisation_count = 0
        self.crane_utilisation_count = 0
        self.charging_point_utilisation_count = 0
        
        # Cargo/Container statistics
        self.cargo_stored = 0
        self.cargo_retrieved = 0
        self.cargo_loaded = 0
        self.cargo_unloaded = 0

        # Port statistics
        self.previous_ship_count_at_port = self.ships_docked_at_port
        self.cargo_volume_in_storage = 0

        # Inefficiencies
        self.delayed_ships = 0
        self.delayed_agvs = 0
        self.out_of_battery_agvs = 0
        self.out_of_battery_cranes = 0


    def step(self):
        """Advance the model by one step."""
        self.reset_model_step_statistics()
        self.schedule.step()
        self.ship_schedules.step()
        self.delayed_ships = self.ship_schedules.get_delayed_ship_count()
        self.datacollector.collect(self)

    # Model is passed into all agents. So Ship Agents can access/modify number of ships at berth
    def get_ships_at_berth(self)-> int:
        return self.previous_ship_count_at_port

    def increment_ships_at_berth(self):
        self.ships_docked_at_port += 1
    
    def decrement_ships_at_berth(self):
        self.ships_docked_at_port -= 1

    # def increment_delayed_ship(self):
    #     self.delayed_ships += 1

    # def increment_delayed_agv(self):
    #     self.delayed_agvs += 1


