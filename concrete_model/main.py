from calvin import *

calvin = CALVIN('links.csv',)

calvin.create_pyomo_model(debug_mode=False)
calvin.solve_pyomo_model(solver='glpk', nproc=1, debug_mode=False)

# this will append to results files
postprocess(calvin.df, calvin.model, resultdir='results') 
