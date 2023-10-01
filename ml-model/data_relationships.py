"""
Determine the relationships between the data.
"""
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

DATASET_PATH = r'datasets\historical_vessel_arrivial.csv'
data = pd.read_csv(DATASET_PATH)

# create a figure and axis
fig, ax = plt.subplots()

# scatter the sepal_length against the sepal_width
ax.scatter(data['num_containers'], data['World Economic Growth Rate(%)'])
# set a title and labels
ax.set_title('Dataset')
ax.set_xlabel('num_containers')
ax.set_ylabel('World Economic Growth Rate(%)')

plt.show()