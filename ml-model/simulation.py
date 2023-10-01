from agent_based_model import *
import pandas as pd
import numpy as np
import sys
import schedules
np.set_printoptions(threshold=sys.maxsize)


NUMBER_OF_RUNS = 2000

# Load data
DATASET_PATH = r'datasets\container_time.csv'
container_schedule_data = pd.read_csv(DATASET_PATH).to_numpy()

# Setup model
ship_schedules = ShipSchedules(container_schedule_data) 
simulation = PortModel(200, 200, 200, ship_schedules)

# Need to implement run method
for i in range(NUMBER_OF_RUNS):
    print(f"Step {i}, time = {simulation.ship_schedules.time}")
    simulation.step()
    

    # update visuals
data = simulation.datacollector.get_model_vars_dataframe().reset_index()
print(data)

data = simulation.datacollector.get_agent_vars_dataframe().reset_index()
print(data)