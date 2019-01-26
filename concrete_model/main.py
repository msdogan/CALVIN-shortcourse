from calvin import *

# specify data file
calvin = CALVIN('links_infeasible.csv')

# create pyomo model from specified data file
calvin.create_pyomo_model(debug_mode=True)

# solve the problem
calvin.solve_pyomo_model(solver='glpk', nproc=1, debug_mode=True)

# postprocess results to create time-series files
postprocess(calvin.df, calvin.model, resultdir='results3')
