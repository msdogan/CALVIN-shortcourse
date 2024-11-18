from calvin import *

# specify data file
calvin = CALVIN('links_example1.csv')

# create pyomo model from specified data file
calvin.create_pyomo_model()

# solve the problem
calvin.solve_pyomo_model(solver='glpk', nproc=1, tee=False, save_json=True)

# postprocess results to create time-series files
postprocess(calvin.df, calvin.model, resultdir='results')
