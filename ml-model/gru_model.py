"""
Train a GRU (Gated Recurrent Unit) to predict ship arrival times.
"""

import numpy as np
import pandas
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow import keras
from keras import layers

DATASET_PATH = r'datasets\historical_vessel_arrivial.csv'

# Hyperparameters
N_TIMESTEPS = 100 # number of time steps to take in to predict the value at the next time step
NUMBER_OF_FEATURES = 5
EPOCHS = 10
BATCH_SIZE = 64

# Add layers to RNN model
model = keras.Sequential()
model.add(layers.GRU(64, input_shape=(N_TIMESTEPS, NUMBER_OF_FEATURES)))
model.add(layers.BatchNormalization())
model.add(layers.Dense(1))
print(model.summary())

# Load dataset
vessel_arrival = pandas.read_csv(DATASET_PATH)
# FIXME: Cannot convert string to float for 'Weather'
data = vessel_arrival[['timestamp', 'num_containers', 'Temperature(°C)', 'Humidity(%)', 'Fuel Price', 'World Economic Growth Rate(%)']].to_numpy().astype('float32')
# data_x = data[:, 1:]
# data_y = data[:, 0]
# print(data_x.shape)
# print(data_y.shape)

# Feature scaling
data = StandardScaler().fit_transform(data)
print(data)

# Feature engineering of data
# Change to sequences of size N_TIMESTEPS
data_sequences = np.lib.stride_tricks.sliding_window_view(data, N_TIMESTEPS + 1, axis = 0)
print(data_sequences.shape)

# Reshape data
data_sequences = data_sequences.reshape(len(data_sequences), N_TIMESTEPS + 1, NUMBER_OF_FEATURES + 1) # FIXME: Hardcoded
print(data_sequences.shape)
data_x = data_sequences[:,:N_TIMESTEPS,1:]
data_y = data_sequences[:,:,0]

# TODO: Normalize time so that it is offsets of each other rather than having a fixed starting time... #todo

# Split dataset
x_train, x_test, y_train, y_test = train_test_split(data_x, data_y, test_size=0.3, random_state=42)
x_validate, y_validate = x_test[:-10], y_test[:-10]
x_test, y_test = x_test[-10:], y_test[-10:]

# Compile the GRU RNN
model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])

# Train and fit GRU RNN model
model.fit(
    x_train, y_train, validation_data=(x_validate, y_validate), batch_size=BATCH_SIZE, epochs=EPOCHS
)

# Test the GRU model
test_loss, test_accuracy = model.evaluate(x_test, y_test)
print(f"Loss: {test_loss}, Accuracy: {test_accuracy}")

# Make predictions
# predictions = model.predict(X_new_data)