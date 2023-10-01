"""
Train a GRU (Gated Recurrent Unit) to predict ship arrival times.
"""
# FIXME: Model works but is not accurate.

import numpy as np
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras
from keras import layers
# np.set_printoptions(threshold=sys.maxsize)

DATASET_PATH = r'datasets\cleaned_data.csv'

# Hyperparameters
N_TIMESTEPS = 30 # number of time steps to take in to predict the value at the next time step
EPOCHS = 10
BATCH_SIZE = 64

# Load dataset
vessel_arrival = pd.read_csv(DATASET_PATH)
# FIXME: Cannot convert string to float for 'Weather'
# Note: we are not getting timestamp as the output, as there is no relationship between timestamp and the features. 
# data = vessel_arrival[['num_containers', 'Temperature(°C)', 'Humidity(%)', 'Fuel Price', 'World Economic Growth Rate(%)']].to_numpy().astype('float32')
data = vessel_arrival[['day_of_month', 'month', 'year','num_containers', 'Temperature(°C)', 'Humidity(%)', 'Fuel Price', 'World Economic Growth Rate(%)', 'weather_1']].to_numpy().astype('int32')
NUMBER_OF_FEATURES = len(data[0]) - 1
# data_x = data[:, 1:]
# data_y = data[:, 0]
# print(data_x.shape)
# print(data_y.shape)

# Feature scaling
# print(data)
data = data / np.linalg.norm(data, axis = 0)
# print(data)

# Feature engineering of data
# Change to sequences of size N_TIMESTEPS
data_sequences = np.lib.stride_tricks.sliding_window_view(data, N_TIMESTEPS + 1, axis = 0)
print(data_sequences.shape)

# Reshape data
print(data_sequences.shape)
data_sequences = data_sequences.reshape(len(data_sequences), N_TIMESTEPS + 1, NUMBER_OF_FEATURES + 1) # FIXME: Hardcoded
print(data_sequences.shape)
data_x = data_sequences[:,:N_TIMESTEPS,1:]
data_y = data_sequences[:,:,0]

# Split dataset
x_train, x_test, y_train, y_test = train_test_split(data_x, data_y, test_size=0.3, random_state=42)
x_validate, y_validate = x_test[:-10], y_test[:-10]
x_test, y_test = x_test[-10:], y_test[-10:]

# Add layers to RNN model
model = keras.Sequential()
model.add(layers.GRU(64, input_shape=(N_TIMESTEPS, NUMBER_OF_FEATURES)))
model.add(layers.BatchNormalization())
model.add(layers.Dense(1))
print(model.summary())

# Compile the GRU RNN
model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])

# Train and fit GRU RNN model
model.fit(
    x_train, y_train, validation_data=(x_validate, y_validate), batch_size=BATCH_SIZE, epochs=EPOCHS
)

# Test the GRU model
print("Test data:")
test_loss, test_accuracy = model.evaluate(x_test, y_test)

# Make predictions
# predictions = model.predict(X_new_data)