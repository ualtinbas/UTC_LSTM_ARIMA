# Libraries

import gurobipy as gp
from gurobipy import GRB
import time

# Time tracking
start_time = time.time()

# Problem Formulation

mdl = gp.Model(name = "Carpenter Problem")

# Variables

var_name_01 = "table_number"
var_01 = mdl.addVar(lb = 0, name = var_name_01,vtype = GRB.INTEGER)

var_name_02 = "bookcase_number"
var_02 = mdl.addVar(lb = 0, name = var_name_02, vtype = GRB.INTEGER)

# Constraints

mdl.addConstr(10*var_01 + 20*var_02 <= 200)
mdl.addConstr(5*var_01 + 4*var_02 <= 80)

# Objective Function

profit = 180*var_01 + 200*var_02
mdl.setObjective(profit, GRB.MAXIMIZE)

# Solve the problem

mdl.optimize()

# Display variables

if mdl.SolCount == 0:
    print("Model is infeasible")
    mdl.computeIIS()
    mdl.write("model_iis.ilp")
else:
    for v in mdl.getVars():
        print(f"{v.VarName} = {v.X}")

# End time tracking
end_time = time.time()

# Print total elapsed time
elapsed_time = end_time - start_time
print(f"\nTotal Execution Time: {elapsed_time:.2f} seconds")

