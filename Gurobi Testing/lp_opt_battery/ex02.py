import matplotlib.pyplot as plt
import numpy as np

import gurobipy as gp
from gurobipy import GRB

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

# Program

file_name = "Gurobi Testing/lp_opt_battery/inputs/ebus_power.txt"
cons_power = load_data(file_name)

file_name = "Gurobi Testing/lp_opt_battery/inputs/electricity_price.txt"
elec_price = load_data(file_name)

file_name = "Gurobi Testing/lp_opt_battery/inputs/pv_power.txt"
pv_power = load_data(file_name)

# Optimization

mdl = gp.Model(name = "Cost Minimization")

# Variables

var_name_pv_power = "pv_power"
var_pv_power = mdl.addVars(sim_len , lb = np.zeros(sim_len), ub = pv_power, name = var_name_pv_power, vtype = GRB.CONTINUOUS)

var_name_battery_charging_power = "battery_charging_power"
var_battery_charging_power = mdl.addVars(sim_len, lb = np.zeros(sim_len), ub = battery_power_max, name = var_name_battery_charging_power, vtype = GRB.CONTINUOUS)

var_name_battery_discharging_power = "battery_discharging_power"
var_battery_discharging_power = mdl.addVars(sim_len, lb = np.zeros(sim_len), ub = battery_power_max, name = var_name_battery_discharging_power, vtype = GRB.CONTINUOUS)

var_name_grid_buying_power = "grid_buying_power"
var_grid_buying_power = mdl.addVars(sim_len, lb = np.zeros(sim_len), ub = grid_power_max, name = var_name_grid_buying_power, vtype = GRB.CONTINUOUS)

var_name_grid_selling_power = "grid_selling_power"
var_grid_selling_power = mdl.addVars(sim_len, lb = np.zeros(sim_len), ub = grid_power_max, name = var_name_grid_selling_power, vtype = GRB.CONTINUOUS)

var_name_battery_soc = "battery_soc"
var_battery_soc = mdl.addVars(sim_len, lb = np.ones(sim_len)*0.1, ub = np.ones(sim_len)*0.9, name = var_name_battery_soc, vtype = GRB.CONTINUOUS)

var_name_battery_charging_bin = "battery_charging_bin"
var_battery_charging_bin = mdl.addVars(sim_len, name = var_name_battery_charging_bin, vtype = GRB.BINARY)

var_name_battery_discharging_bin = "battery_discharging_bin"
var_battery_discharging_bin = mdl.addVars(sim_len, name = var_name_battery_discharging_bin, vtype = GRB.BINARY)

var_name_grid_buying_bin = "grid_buying_bin"
var_grid_buying_bin = mdl.addVars(sim_len, name = var_name_grid_buying_bin, vtype = GRB.BINARY)

var_name_grid_selling_bin = "grid_selling_bin"
var_grid_selling_bin = mdl.addVars(sim_len, name = var_name_grid_selling_bin, vtype = GRB.BINARY)

# Constraints

for t in range(0, sim_len):
    if t == 0:
        mdl.addConstr(var_battery_soc[t] == init_soc + (var_battery_charging_power[t]*bat_eff - var_battery_discharging_power[t]/bat_eff)*delta_t/battery_capacity)
    else:
        mdl.addConstr(var_battery_soc[t] == var_battery_soc[t-1] + (var_battery_charging_power[t]*bat_eff - var_battery_discharging_power[t]/bat_eff)*delta_t/battery_capacity)

for t in range(0, sim_len):
    mdl.addConstr(cons_power[t] - var_pv_power[t] + var_battery_charging_power[t] - var_battery_discharging_power[t] == var_grid_buying_power[t] - var_grid_selling_power[t])

for t in range(0, sim_len):
    mdl.addConstr(var_battery_charging_bin[t] + var_battery_discharging_bin[t] <= 1)

for t in range(0, sim_len):
    mdl.addConstr(var_battery_charging_power[t] <= var_battery_charging_bin[t]*battery_power_max[t])
    mdl.addConstr(var_battery_discharging_power[t] <= var_battery_discharging_bin[t]*battery_power_max[t])

for t in range(0, sim_len):
    mdl.addConstr(var_grid_buying_bin[t] + var_grid_selling_bin[t] <= 1)

for t in range(0, sim_len):
    mdl.addConstr(var_grid_buying_power[t] <= var_grid_buying_bin[t]*grid_power_max[t])
    mdl.addConstr(var_grid_selling_power[t] <= var_grid_selling_bin[t]*grid_power_max[t])

# Objective Function

cost = 0
for t in range(0, sim_len):
    cost += var_grid_buying_power[t]*elec_price[t] - var_grid_selling_power[t]*np.min(elec_price)*0.1

# Solve problem

mdl.setObjective(cost, GRB.MINIMIZE)
mdl.optimize()

# Display variables

'''
if mdl.SolCount == 0:
    print("Model is infeasible")
    mdl.computeIIS()
    mdl.write("model_iis.ilp")
else:
    for v in mdl.getVars():
        print(f"{v.VarName} = {v.X}")
'''

########################################################################
## Save Results of Optimization
########################################################################


# Pridce profile
file_name = "Gurobi Testing/lp_opt_battery/outputs/electricity_price.txt"
save_data(file_name, elec_price, sim_len)

# Load profile
file_name = "Gurobi Testing/lp_opt_battery/outputs/load_profile.txt"
save_data(file_name, cons_power, sim_len)

# PV profiles (MPPT and used)
file_name = "Gurobi Testing/lp_opt_battery/outputs/pv_profile.txt"
save_data(file_name, pv_power, sim_len)

file_name = "Gurobi Testing/lp_opt_battery/outputs/pv_profile_used.txt"
data = np.zeros(sim_len)
pv_power_used = np.zeros(sim_len)
for t in range(0, sim_len):
    var_name = var_name_pv_power + "[" + str(t)  + "]"
    var_value = mdl.getVarByName(var_name)
    data[t] = var_value.x
    pv_power_used[t] = data[t]
save_data(file_name, data, sim_len)

file_name = "Gurobi Testing/lp_opt_battery/outputs/pv_profile_curtailed.txt"
data = np.zeros(sim_len)
pv_power_curtailed = np.zeros(sim_len)
for t in range(0, sim_len):
    data[t] = pv_power[t] - pv_power_used[t]
    pv_power_curtailed[t] = data[t]
save_data(file_name, data, sim_len)

# Battery profiles (charging, discharging and soc)
file_name = "Gurobi Testing/lp_opt_battery/outputs/battery_profile_charging.txt"
data = np.zeros(sim_len)
battery_power_charging = np.zeros(sim_len)
for t in range(0, sim_len):
    var_name = var_name_battery_charging_power + "[" + str(t)  + "]"
    var_value = mdl.getVarByName(var_name)
    data[t] = var_value.x
    battery_power_charging[t] = data[t]
save_data(file_name, data, sim_len)


file_name = "Gurobi Testing/lp_opt_battery/outputs/battery_profile_discharging.txt"
data = np.zeros(sim_len)
battery_power_discharging = np.zeros(sim_len)
for t in range(0, sim_len):
    var_name = var_name_battery_discharging_power + "[" + str(t)  + "]"
    var_value = mdl.getVarByName(var_name)
    data[t] = var_value.x
    battery_power_discharging[t] = data[t]
save_data(file_name, data, sim_len)


file_name = "Gurobi Testing/lp_opt_battery/outputs/battery_profile_soc.txt"
data = np.zeros(sim_len)
battery_soc = np.zeros(sim_len)
for t in range(0, sim_len):
    var_name = var_name_battery_soc + "[" + str(t)  + "]"
    var_value = mdl.getVarByName(var_name)
    data[t] = var_value.x
    battery_soc[t] = data[t]
save_data(file_name, data, sim_len)

# Grid profiles
file_name = "Gurobi Testing/lp_opt_battery/outputs/grid_profile_buying.txt"
data = np.zeros(sim_len)
grid_power_buying = np.zeros(sim_len)
for t in range(0, sim_len):
    var_name = var_name_grid_buying_power + "[" + str(t)  + "]"
    var_value = mdl.getVarByName(var_name)
    data[t] = var_value.x
    grid_power_buying[t] = data[t]
save_data(file_name, data, sim_len)

file_name = "Gurobi Testing/lp_opt_battery/outputs/grid_profile_selling.txt"
data = np.zeros(sim_len)
grid_power_selling = np.zeros(sim_len)
for t in range(0, sim_len):
    var_name = var_name_grid_selling_power + "[" + str(t)  + "]"
    var_value = mdl.getVarByName(var_name)
    data[t] = var_value.x
    grid_power_selling[t] = data[t]
save_data(file_name, data, sim_len)

########################################################################
## Plot Results of Optimization
########################################################################

plt.subplot(311)
plt.plot(elec_price, label='Electricity price')
plt.legend()
plt.grid()


plt.subplot(312)
plt.plot(cons_power, label='Consumption power')
plt.plot(grid_power_buying,'--', label='Grid power buy')
plt.plot(grid_power_selling,'--', label='Grid power sell')
plt.plot(-pv_power, label='PV power')
plt.plot(-pv_power_used,'--', label = 'PV power used')
plt.plot(battery_power_charging, label = 'Battery power charging')
plt.plot(-battery_power_discharging,'--', label = 'Battery power discharging')
plt.legend()
plt.grid()


plt.subplot(313)
plt.plot(battery_soc, label='Battery soc')
plt.legend()
plt.grid()


plt.legend()
plt.show()