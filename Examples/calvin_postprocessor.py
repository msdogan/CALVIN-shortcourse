#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CALVIN Postprocessor

Created on Tue Sep  3 15:26:51 2024

@author: msdogan

Postprocess following CALVIN results:
    - debug flows (debugsource and debugsink)
    - reservoir storage (surface and groundwater)
    - reservoir release and pumping
    - agricultural and urban deliveries
    - deliveries from surface water and groundwater
    - Delta exports from Banks and Tracy PPs
    - surplus Delta outflow
"""

import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")

fp = 'full_size_model_94_years_10percent_reduced_inflow'

flow = pd.read_csv(fp + '/flow.csv', index_col=0, parse_dates=True)
storage = pd.read_csv(fp + '/storage.csv', index_col=0, parse_dates=True)

links = flow.keys()

resultdir = 'postprocess_'+fp
if not os.path.isdir(resultdir):
  os.makedirs(resultdir)

# links with debug flows
dbugsrc_links = []
dbugsnk_links = []

for link in links:
    i,j=link.split('-')
    if i == 'DBUGSRC':
        dbugsrc_links.append(link)
    if j == 'DBUGSNK':
        dbugsnk_links.append(link)

# links where debug source is positive
dl_src = []
for l in dbugsrc_links:
    if flow[l].sum()>0.00001:
        dl_src.append(l)
dbugsrc = flow[dl_src]
# links where debug sink is positive
dl_snk = []
for l in dbugsnk_links:
    if flow[l].sum()>0.00001:
        dl_snk.append(l)  
dbugsnk = flow[dl_snk]

# save links with debug flows (source or sink)
dbugsrc.to_csv(resultdir+'/debugsource.csv')
dbugsnk.to_csv(resultdir+'/debugsink.csv')

# remove debug links (if any)
flow_no_debug = flow.drop(dbugsrc_links+dbugsnk_links,axis=1)

# reservoir storage
surface_res = pd.DataFrame(index=storage.index)
gw_res = pd.DataFrame(index=storage.index)

reservoirs = storage.keys()
for res in reservoirs:
    if res.split('_')[0] == 'SR':
        surface_res[res]=storage[res]
    if res.split('_')[0] == 'GW':
        gw_res[res]=storage[res]

# you may want to remove reservoirs, like natural lakes
surface_res = surface_res.drop(
    ['SR_BVLB','SR_CR1','SR_CR2','SR_CR3','SR_ML','SR_OL','SR_SS','SR_TL'],
    axis=1)
# save surface reservoir storage
surface_res.to_csv(resultdir+'/reservoir_storage.csv')
# save groundwater storage
gw_res.to_csv(resultdir+'/groundwater_storage.csv')

# reservoir outflow
res_outflow_links = []
for sr in surface_res:
    for link in flow_no_debug:
        i,j=link.split('-')
        if i == sr:
            res_outflow_links.append(link)
res_outflow = flow_no_debug[res_outflow_links]

# save surface reservoir outflows
res_outflow.to_csv(resultdir+'/reservoir_outflow.csv')

# groundwater pumping
gw_pump_links = []
for gw in gw_res:
    for link in flow_no_debug:
        i,j=link.split('-')
        if i == gw:
            gw_pump_links.append(link)
gw_pumping = flow_no_debug[gw_pump_links]

# save groundwater pumping
gw_pumping.to_csv(resultdir+'/groundwater_pumping.csv')

# agricultural deliveries
ag_delivery_links = []
for link in flow_no_debug.keys():
    i,j=link.split('-')
    if i[0] == 'A' and j[:2] == 'HU':
        ag_delivery_links.append(link)
ag_delivery = flow_no_debug[ag_delivery_links]

# save ag delivery
ag_delivery.to_csv(resultdir+'/ag_delivery.csv')

# urban deliveries
urban_delivery_links = []
for link in flow_no_debug.keys():
    i,j=link.split('-')
    if j[:3] == 'INT' or j[:3] == 'EXT' or j[:3] == 'Ext' or j[:3] == 'IND' or j[:3] == 'Ind'or j[:4] == 'ERES' or j[:4] == 'ERes' or j[:4] == 'IRES' or j[:4] == 'IRes':
        urban_delivery_links.append(link)
urban_delivery = flow_no_debug[urban_delivery_links]

# save urban delivery
urban_delivery.to_csv(resultdir+'/urban_delivery.csv')

# ag deliveries from surface water
ag_delivery_sw_links = []
for link in flow_no_debug.keys():
    i,j=link.split('-')
    if i[:3] == 'HSU' and j[0] == 'A':
        ag_delivery_sw_links.append(link)
ag_delivery_sw = flow_no_debug[ag_delivery_sw_links]

# save ag delivery from surface water
ag_delivery_sw.to_csv(resultdir+'/ag_delivery_sw.csv')

# ag deliveries from groundwater
ag_delivery_gw_links = []
for link in flow_no_debug.keys():
    i,j=link.split('-')
    if i[:3] == 'HGP' and j[0] == 'A':
        ag_delivery_gw_links.append(link)
ag_delivery_gw = flow_no_debug[ag_delivery_gw_links]

# save ag delivery from groundwater
ag_delivery_gw.to_csv(resultdir+'/ag_delivery_gw.csv')

# urban deliveries from surface water
urban_delivery_sw_links = []
for link in flow_no_debug.keys():
    i,j=link.split('-')
    if i[:3] == 'WTP' and j[0] == 'U':
        urban_delivery_sw_links.append(link)
urban_delivery_sw = flow_no_debug[urban_delivery_sw_links]

# save urban delivery from surface water
urban_delivery_sw.to_csv(resultdir+'/urban_delivery_sw.csv')

# urban deliveries from groundwater
urban_delivery_gw_links = []
for link in flow_no_debug.keys():
    i,j=link.split('-')
    if i[:3] == 'HGP' and j[0] == 'U':
        urban_delivery_gw_links.append(link)
urban_delivery_gw = flow_no_debug[urban_delivery_gw_links]

# save urban delivery from groundwater
urban_delivery_gw.to_csv(resultdir+'/urban_delivery_gw.csv')

# urban deliveries from wastewater recycled
urban_delivery_rc_links = []
for link in flow_no_debug.keys():
    i,j=link.split('-')
    if i[:3] == 'HNP' or i[:2] == 'HP':
        urban_delivery_rc_links.append(link)
urban_delivery_rc = flow_no_debug[urban_delivery_rc_links]

# save urban delivery from wastewater recycled
urban_delivery_rc.to_csv(resultdir+'/urban_delivery_rc.csv')

# Delta exports
delta_exports = flow_no_debug[['PMP_Banks-D800','PMP_Tracy-D701']]

# save Delta exports
delta_exports.to_csv(resultdir+'/delta_exports.csv')

# surplus Delta outflow
surplus_delta_outflow = flow_no_debug['Surp_Delta-SINK']

# save surplus Delta outflow
surplus_delta_outflow.to_csv(resultdir+'/surplus_delta_outflow.csv')

# RIM inflow (This is actually input)
rim_inflow_links = []
for link in flow_no_debug.keys():
    i,j=link.split('-')
    if i[:6] == 'INFLOW' and j[:2] == 'SR':
        rim_inflow_links.append(link)
rim_inflow = flow_no_debug[rim_inflow_links]

rim_inflow = rim_inflow.drop(
    ['INFLOW-SR_CR3'],
    axis=1)
# save rim inflow data
rim_inflow.to_csv(resultdir+'/rim_inflow.csv')

# Groundwater inflow (This is actually input)
gw_inflow_links = []
for link in flow_no_debug.keys():
    i,j=link.split('-')
    if i[:6] == 'INFLOW' and j[:2] == 'GW':
        gw_inflow_links.append(link)
gw_inflow = flow_no_debug[gw_inflow_links]

# save gw inflow data
gw_inflow.to_csv(resultdir+'/gw_inflow.csv')