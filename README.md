# CALVIN Summer 2020 Shortcourse

This is a short course intended for those who are interested in large-scale water optimization modeling with CALVIN model. Some basic optimization knowledge, especially linear programming, is assumed. This crash course introduces basics of CALVIN model with Pyomo modeling environment. CALVIN is a large-scale hydroeconomic optimization model for California, aiming to optimize water allocation to users. CALVIN is the same model as CALVIN but modeled in a different environment employing different solvers. It is an integrated model with surface and groundwater representation, covering California's most water and water-related economic activities.
*********************************
# Registration:

Registration is free of charge but please fill out registration form

https://forms.gle/GoEGirVznrmp9HHm7

*********************************
# Location:

Online - Zoom Meetings

https://ucmerced.zoom.us/j/97664369012?pwd=Q3ppSGxBUDI1NDF6MkFFVFlCUnZnQT09 

Meeting ID: 976 6436 9012
Passcode: CALVIN2020

*********************************
# CALVIN website:
See CALVIN website for documentation and more information

https://watershed.ucdavis.edu/shed/lund/CALVIN/

# Related GitHub repositories:

## CALVIN main repository

This repository has CALVIN's model structure, including decision variables, objective function and constraints. There are also example runs and some brief documentation.

https://github.com/ucd-cws/calvin

## HOBBES database

HOBBES database hosting CALVIN network data. Database includes California's water infrastructure data (capacities, network properties etc) and hydrology data (inflow, groundwater etc.)

https://github.com/ucd-cws/calvin-network-data

## CALVIN network tools

CALVIN network tool is used to export water network matrix of California from HOBBES database in a format that CALVIN python version can read.

https://github.com/ucd-cws/calvin-network-tools

## Some postprocessed results

Change in California's overall surface water storage over the 82-year period:

![Example](Examples/full_size_model/sr.gif)

Change in California's overall groundwater storage over the 82-year period:

![Example](Examples/full_size_model/gw.gif)

Water deliveries to agricultural and urban users 
(USV: Upper Sacramento Valley; LSVD: Lower Sacramento Valley and Delta; SJSB: San Joaquin and South Bay; TB: Tulare Basin; SC: Southern California

![Example](Examples/full_size_model/portfolio.png)
