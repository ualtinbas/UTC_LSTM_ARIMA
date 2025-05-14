import gymnasium as gym
import numpy as np
import random
import time

# Self-defined function
def load_data(file_name):
    data_set = np.loadtxt(file_name)
    data_length = len(data_set)
    data_info = np.zeros(data_length)

    for t in range(0, data_length):
        data_info[t] = float(data_set[t])
    
    return data_info

# Saving data
def save_data(fileName, data, sim_len):
    
    fid = open(fileName,"w")
    for t in range(0, sim_len):
        fid.write(str(data[t]) + "\n")
    fid.close()

# Constants
sim_len = 144
delta_t = 24/sim_len

init_soc = 0.9
bat_eff = 0.95
battery_capacity = 500000*1000

battery_power_max = np.ones(sim_len)*100000
grid_power_max = np.ones(sim_len)*200000

# Files
file_name = "battery_inputs/ebus_power.txt"
cons_power = load_data(file_name)

file_name = "battery_inputs/electricity_price.txt"
elec_price = load_data(file_name)

file_name = "battery_inputs/pv_power.txt"
pv_power = load_data(file_name)

# Define the Environment
# class BatteryEnv: