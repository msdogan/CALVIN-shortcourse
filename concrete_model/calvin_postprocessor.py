#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CALVIN Postprocessor

Created on Tue Sep  3 15:26:51 2024
Improved version. Date: 14/04/2026

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
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

"""
-----------------------
 PATHS
-----------------------
"""
fp = Path('results_1921_1922_debug')
resultdir = Path(f'postprocess_{fp}')
resultdir.mkdir(parents=True, exist_ok=True)

"""
-----------------------
 LOAD DATA
-----------------------
 flow and storage are CALVIN outputs
 scarcity = target - delivery
""" 
flow = pd.read_csv(fp / 'flow.csv', index_col=0, parse_dates=True)
storage = pd.read_csv(fp / 'storage.csv', index_col=0, parse_dates=True)
scarcity_vol = pd.read_csv(fp / 'shortage_volume.csv', index_col=0, parse_dates=True)
scarcity_cost = pd.read_csv(fp / 'shortage_cost.csv', index_col=0, parse_dates=True)

# ag_target = pd.read_csv('ubt_ag_target_apr142026.csv', index_col=0, parse_dates=True)
# urban_target = pd.read_csv('ubt_urban_target.csv', index_col=0, parse_dates=True)

"""
-----------------------
 PREPROCESS LINKS
-----------------------
split links into origin and terminal nodes 
""" 
link_df = flow.columns.to_series().str.split('-', expand=True)
link_df.columns = ['orgn', 'term']

# -----------------------
# HELPER FUNCTIONS
# -----------------------
def save(df, name):
    df.to_csv(resultdir / f"{name}.csv", float_format="%.2f")

def filter_links(flow_df, link_df, orgn_prefix=None, term_prefix=None):
    mask = pd.Series(True, index=link_df.index)
    if orgn_prefix:
        mask &= link_df['orgn'].str.startswith(orgn_prefix)
    if term_prefix:
        mask &= link_df['term'].str.startswith(term_prefix)
    return flow_df.loc[:, mask]

"""
-----------------------
 DEBUG LINKS
-----------------------
"""
dbugsrc_links = link_df[link_df['orgn'] == 'DBUGSRC'].index
dbugsnk_links = link_df[link_df['term'] == 'DBUGSNK'].index

dbugsrc = flow[dbugsrc_links].loc[:, lambda df: df.sum() > 1e-5]
dbugsnk = flow[dbugsnk_links].loc[:, lambda df: df.sum() > 1e-5]

save(dbugsrc, 'debugsource')
save(dbugsnk, 'debugsink')

# remove debug links
flow_no_debug = flow.drop(columns=list(dbugsrc_links) + list(dbugsnk_links), errors='ignore')

"""
-----------------------
 STORAGE (Surface and Groundwater)
-----------------------
"""
surface_res = storage.filter(regex='^SR_').copy()
gw_res = storage.filter(regex='^GW_').copy()

drop_res = ['SR_BVLB','SR_CR1','SR_CR2','SR_CR3','SR_ML','SR_OL','SR_SS','SR_TL'] # do not want to see these reservoirs' storage
surface_res = surface_res.drop(columns=drop_res, errors='ignore')

save(surface_res, 'reservoir_storage')
save(gw_res, 'groundwater_storage')

"""
-----------------------
 RESERVOIR OUTFLOW & PUMPING
-----------------------
"""
res_outflow = flow_no_debug.loc[:, link_df['orgn'].isin(surface_res.columns)]
gw_pumping = flow_no_debug.loc[:, link_df['term'].isin(gw_res.columns)]

save(res_outflow, 'reservoir_outflow')
save(gw_pumping, 'groundwater_pumping')

"""
-----------------------
 AGRICULTURAL DELIVERY & SCARCITY
-----------------------
"""
ag_delivery = filter_links(flow_no_debug, link_df, 'A', 'HU')
save(ag_delivery, 'ag_delivery_total')

ag_delivery_separated = flow_no_debug.loc[:, link_df['orgn'].str.startswith(('HU'))]
ag_delivery_separated = ag_delivery_separated.drop(columns=['HU500-AgS_Owens'], errors='ignore') # Remove Owens ag delivery, fixed & no economics
save(ag_delivery_separated, 'ag_delivery_separated')

# ag_scarcity = (ag_target - ag_links).clip(lower=0)
# ag_scarcity_percent = (ag_scarcity / ag_target * 100).clip(lower=0)

ag_scarcity = scarcity_vol.loc[:,ag_delivery_separated.columns]
ag_target = ag_delivery_separated + ag_scarcity
ag_scarcity_percent = (ag_scarcity / ag_target * 100).clip(lower=0)

save(ag_scarcity, 'ag_scarcity')
save(ag_scarcity_percent, 'ag_scarcity_percent')

"""
-----------------------
 URBAN DELIVERY & SCARCITY
-----------------------
"""
urban_mask = (link_df['term'].str.startswith(('INT','EXT','Ext','IND','Ind','ERES','ERes','IRES','IRes')))
urban_delivery = flow_no_debug.loc[:, urban_mask]
save(urban_delivery, 'urban_delivery')

urban_scarcity = scarcity_vol.loc[:,urban_mask]
urban_target = urban_delivery + urban_scarcity
urban_scarcity_percent = (urban_scarcity / urban_target * 100).clip(lower=0)

save(urban_scarcity, 'urban_scarcity')
save(urban_scarcity_percent, 'urban_scarcity_percent')

"""
-----------------------
 SOURCE TYPES (Delivery Portfolio)
-----------------------
Agriculture: surface and groundwater deliveries
Urban: surface, groundwater and recycled water deliveries
"""
ag_delivery_sw = filter_links(flow_no_debug, link_df, 'HSU', 'A')
ag_delivery_gw = filter_links(flow_no_debug, link_df, 'HGP', 'A')

urban_delivery_sw = filter_links(flow_no_debug, link_df, 'WTP', 'U')
urban_delivery_gw = filter_links(flow_no_debug, link_df, 'HGP', 'U')
urban_delivery_rc = flow_no_debug.loc[:, link_df['term'].str.startswith(('HNP','HP'))]

save(ag_delivery_sw, 'ag_delivery_sw')
save(ag_delivery_gw, 'ag_delivery_gw')
save(urban_delivery_sw, 'urban_delivery_sw')
save(urban_delivery_gw, 'urban_delivery_gw')
save(urban_delivery_rc, 'urban_delivery_rc')

"""
-----------------------
 DELTA WATER OPERATIONS
-----------------------
Delta exports (from Banks and Tracy PP)
Surplus Delta outflow
"""
delta_exports = flow_no_debug.reindex(columns=['PMP_Banks-D800','PMP_Tracy-D701'])
save(delta_exports, 'delta_exports')

surplus_delta_outflow = flow_no_debug.get('Surp_Delta-SINK', pd.Series(index=flow.index))
save(surplus_delta_outflow, 'surplus_delta_outflow')

"""
-----------------------
 INFLOWS
-----------------------
These are inputs
"""
rim_mask = (link_df['orgn'].str.startswith('INFLOW')) & (link_df['term'].str.startswith('SR'))
rim_inflow = flow_no_debug.loc[:, rim_mask].drop(columns=['INFLOW-SR_CR3'], errors='ignore') # Colorado River water
save(rim_inflow, 'rim_inflow')

gw_mask = (link_df['orgn'].str.startswith('INFLOW')) & (link_df['term'].str.startswith('GW'))
gw_inflow = flow_no_debug.loc[:, gw_mask]
save(gw_inflow, 'gw_inflow')
