#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  2 15:36:57 2025

@author: msdogan
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

# print(plt.style.available)
plt.style.use('ggplot')

fps = {
       'postprocess_network_1921_2015_basecase': 'Basecase w/ overdraft',
       'postprocess_network_1921_2015_basecase_no_overdraft_debug': 'Basecase w/o overdraft',
        'postprocess_network_KACE-1-0-G_ssp585_no_overdraft_debug':'KACE-1-0-G_ssp585 (wettest)',
        # 'postprocess_network_TaiESM1_ssp245_no_overdraft_debug':'TaiESM1_ssp245 (2nd wettest)',
        'postprocess_network_MPI-ESM1-2-HR_ssp585_no_overdraft_debug':'MPI-ESM1-2-HR_ssp585 (driest)',
        # 'postprocess_network_MRI-ESM2-0_ssp245_no_overdraft_debug':'MRI-ESM2-0_ssp245 (2nd driest)',
       }

alpha = 0.65 # transparency

# plot time-series
def ts_plotter(file,title,ylabel,savepath,fps,tot_sum=True,col=None,factor=12):
    fig,ax = plt.subplots(figsize=(5,4))
    for i,fp in enumerate(fps):
        data = pd.read_csv(fp + '/'+file, index_col=0, parse_dates=True)
        if tot_sum:
            cols = data.columns
            plot_data = data[cols].sum(axis=1)
            annual_avg = plot_data.groupby(plot_data.index.year).mean()*factor
        else:
            plot_data = data[col]
            annual_avg = plot_data.groupby(plot_data.index.year).mean()*factor
        plt.plot(annual_avg, label=fps[fp],alpha=alpha)
    plt.xticks()
    plt.yticks()
    plt.legend(frameon=True)
    ax.patch.set(lw=2, ec='black')
    plt.xlim([annual_avg.index.min()+1,annual_avg.index.max()-1]) # data is based on water year
    plt.xlabel('Year')
    plt.ylabel(ylabel)
    plt.title(title,loc='left',fontweight='bold')
    plt.tight_layout()
    plt.savefig(savepath, transparent=False, dpi=300)
    plt.close(fig)
    return

# plot delivery-duration
def duration_plotter(file,title,ylabel,savepath,fps,tot_sum=True,col=None,yscalelog=False):
    fig,ax = plt.subplots(figsize=(5,4))
    for i,fp in enumerate(fps):
        data = pd.read_csv(fp + '/'+file, index_col=0, parse_dates=True)
        if tot_sum:
            cols = data.columns
            plot_data = data[cols].sum(axis=1)
        else:
            plot_data = data[col]
        sort = np.sort(plot_data)[::-1]
        exceedence = np.arange(1.,len(sort)+1) / len(sort)
        plt.plot(exceedence*100, sort, label=fps[fp],alpha=alpha)
    plt.xticks(np.arange(0,101,10))
    plt.yticks()
    plt.legend(frameon=True)
    ax.patch.set(lw=2, ec='black')
    plt.xlabel('Exceedance (%)')
    plt.ylabel(ylabel)
    if yscalelog:
        ax.set_yscale('log')
    plt.title(title,loc='left',fontweight='bold')
    plt.tight_layout()
    plt.savefig(savepath, transparent=False,dpi=300)
    plt.close(fig)

# plot monthly average
def monthly_average(file,title,ylabel,savepath,fps,col=None,kind='bar'):
    fig,ax = plt.subplots(figsize=(5,4))
    plot_data = pd.DataFrame()
    for i,fp in enumerate(fps):
        data = pd.read_csv(fp + '/'+file, index_col=0, parse_dates=True)
        total_sum = data.sum(axis=1)
        monthly_avg = total_sum.groupby(total_sum.index.month).mean()
        plot_data[fps[fp]] = monthly_avg
    plot_data.index = monthly_avg.index
    plot_data.index.name = 'Month'
    plot_data.plot(kind=kind,ax=ax,rot=0,alpha=alpha)
    plt.xticks()
    plt.yticks()
    plt.legend(frameon=True)
    ax.patch.set(lw=2, ec='black')
    plt.xlabel('Month')
    plt.ylabel(ylabel)
    plt.title(title,loc='left',fontweight='bold')
    plt.tight_layout()
    plt.savefig(savepath, transparent=False,dpi=300)
    plt.close(fig)

# plot time-series (for change in storage)
def ts_delta_stor_plotter(file,title,ylabel,savepath,fps,tot_sum=True,col=None):
    fig,ax = plt.subplots(figsize=(5,4))
    for i,fp in enumerate(fps):
        data = pd.read_csv(fp + '/'+file, index_col=0, parse_dates=True)
        if tot_sum:
            cols = data.columns
            plot_data = data[cols].sum(axis=1)
        else:
            plot_data = data[col]
        plt.plot(plot_data-plot_data.iloc[0], label=fps[fp],alpha=alpha)
    plt.xticks()
    plt.yticks()
    plt.legend(frameon=True)
    ax.patch.set(lw=2, ec='black')
    plt.xlabel('Time')
    plt.ylabel(ylabel)
    plt.title(title,loc='left',fontweight='bold')
    plt.tight_layout()
    plt.savefig(savepath, transparent=False, dpi=300)
    plt.close(fig)
    return

def annual_average(file,title,ylabel,xlabel,savepath,fps,col=None,kind='bar',factor=12,yscalelog=False):
    fig,ax = plt.subplots(figsize=(8,4))
    plot_data = pd.DataFrame()
    for i,fp in enumerate(fps):
        data = pd.read_csv(fp + '/'+file, index_col=0, parse_dates=True)
        total_annual = data.mean(axis=0)*factor
        plot_data[fps[fp]] = total_annual
    plot_data.index = total_annual.index
    plot_data.index.name = ylabel
    plot_data.to_csv(f'{savepath}.csv')
    plot_data.plot(kind=kind,ax=ax,rot=0,alpha=alpha)
    plt.xticks(rotation=90)
    plt.yticks()
    if yscalelog:
        ax.set_yscale('log')
    plt.legend(frameon=True)
    ax.patch.set(lw=2, ec='black')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title,loc='left',fontweight='bold')
    plt.tight_layout()
    plt.savefig(savepath, transparent=False,dpi=300)
    plt.close(fig)

# plot violin distribution
def violin_plotter(file,title,ylabel,savepath,fps,tot_sum=True,col=None):
    fig,ax = plt.subplots(figsize=(5,6))
    plot_data = pd.DataFrame()
    for i,fp in enumerate(fps):
        data = pd.read_csv(fp + '/'+file, index_col=0, parse_dates=True)
        if tot_sum:
            cols = data.columns
            plot_data[fps[fp]] = data[cols].sum(axis=1)
        else:
            plot_data[fps[fp]] = data[col]
    position = [2*i+2 for i in range(len(fps))]
    label = [fps[fp] for i,fp in enumerate(fps)]
    vp = ax.violinplot(plot_data, position, widths=2,
                   showmeans=False, showmedians=True, showextrema=True)
    plt.xticks(position,label,rotation=90)
    plt.yticks()
    ax.patch.set(lw=2, ec='black')
    plt.xlabel('Scenario')
    plt.ylabel(ylabel)
    plt.title(title,loc='left',fontweight='bold')
    plt.tight_layout()
    plt.savefig(savepath, transparent=False, dpi=300)
    plt.close(fig)
    return

def avg_value_table(file,index_name,savepath,fps,tot_sum=True,col=None):
    save_data = pd.DataFrame()
    for i,fp in enumerate(fps):
        data = pd.read_csv(fp + '/'+file, index_col=0, parse_dates=True)
        if tot_sum:
            cols = data.columns
            get_data = data[cols].sum(axis=1)
        else:
            get_data = data[col]
        save_data[fps[fp]] = get_data.mean(axis=0)
    save_data.index.name = index_name
    save_data.to_csv(savepath)

'''
Reservoir Storage
'''
print('Reservoir Operations')
save_dir = 'plots/surface_reservoirs'
os.makedirs(save_dir, exist_ok=True)



# Reservoir Storage
ts_plotter(file='reservoir_storage.csv',title='Annual Surface Storage',ylabel='Storage (TAF)',savepath=f'{save_dir}/surface_storage.png',fps=fps,factor=1)
# Reservoir Storage Duration
duration_plotter(file='reservoir_storage.csv',title='Monthly Surface Storage',ylabel='Storage (TAF)',savepath=f'{save_dir}/surface_storage_duration.png',fps=fps)
# Reservior Monthly Storage
monthly_average(file='reservoir_storage.csv',title='Monthly Surface Storage',ylabel='Storage (TAF)',savepath=f'{save_dir}/surface_storage_monthly_average.png',fps=fps,kind='line')
# Annual Storage for each Reservoir
annual_average(file='reservoir_storage.csv',title='Annual Surface Storage',ylabel='Storage (TAF)',xlabel='Reservoir',savepath=f'{save_dir}/surface_storage_annual_average.png',fps=fps,kind='bar',factor=1,yscalelog=False)
# Monthly Storage Violin Distribution
violin_plotter(file='reservoir_storage.csv',title='Monthly Surface Storage',ylabel='Storage (TAF)',savepath=f'{save_dir}/surface_storage_violin.png',fps=fps)

# Individual Reservoir Storage
reservoirs = {
    'SR_SHA':'Shasta',
    'SR_FOL':'Folsom',
    'SR_ORO':'Oroville',
    'SR_MIL':'Millerton',
    'SR_CLE':'Trinity',
    'SR_SNL':'San Luis'
    }
for col in reservoirs:
    # time-series
    ts_plotter(file='reservoir_storage.csv',title=reservoirs[col]+' Annual Storage',ylabel='Storage (TAF)',savepath=f'{save_dir}/storage_{reservoirs[col]}.png',fps=fps,tot_sum=False,col=col,factor=1)
    # storage duration
    duration_plotter(file='reservoir_storage.csv',title=reservoirs[col]+' Monthly Storage',ylabel='Storage (TAF)',savepath=f'{save_dir}/storage_duration_{reservoirs[col]}.png',fps=fps,tot_sum=False,col=col)

# # avg_value_table(file='reservoir_storage.csv',index_name='storage (TAF)',savepath=f'{save_dir}/average_storage.csv',fps=fps,tot_sum=True,col=None)

'''
Reservoir Release
'''
# Reservoir Release
ts_plotter(file='reservoir_outflow.csv',title='Annual Reservoir Release',ylabel='Flow (TAF/y)',savepath=f'{save_dir}/surface_release.png',fps=fps,factor=12)
# Reservoir Release Duration
duration_plotter(file='reservoir_outflow.csv',title='Monthly Reservoir Release',ylabel='Flow (TAF/m)',savepath=f'{save_dir}/reservoir_release_duration.png',fps=fps,yscalelog=True)
# Reservior Monthly Release
monthly_average(file='reservoir_outflow.csv',title='Monthly Reservoir Release',ylabel='Flow (TAF/m)',savepath=f'{save_dir}/reservoir_release_monthly_average',fps=fps)
# Monthly Release Violin Distribution
violin_plotter(file='reservoir_outflow.csv',title='Monthly Reservoir Release',ylabel='Flow (TAF/m)',savepath=f'{save_dir}/reservoir_release_violin.png',fps=fps)

# Individual Reservoir Release
reservoirs = {
    'SR_SHA-D5':'Shasta',
    'SR_FOL-D9':'Folsom',
    'SR_ORO-C23':'Oroville',
    'SR_MIL-D605':'Millerton',
    'SR_CLE-D94':'Trinity',
    }
for col in reservoirs:
    # time-series
    ts_plotter(file='reservoir_outflow.csv',title=reservoirs[col]+' Annual Release',ylabel='Flow (TAF/y)',savepath=f'{save_dir}/release_{reservoirs[col]}.png',fps=fps,tot_sum=False,col=col,factor=12)
    # release duration
    duration_plotter(file='reservoir_outflow.csv',title=reservoirs[col]+' Monthly Release',ylabel='Flow (TAF/m)',savepath=f'{save_dir}/release_duration_{reservoirs[col]}.png',fps=fps,tot_sum=False,col=col,yscalelog=True)

'''
Groundwater Storage
'''
print('Groundwater')
save_dir = 'plots/groundwater'
os.makedirs(save_dir, exist_ok=True)

# Groundwater Storage
ts_plotter(file='groundwater_storage.csv',title='Annual Groundwater Storage',ylabel='Storage (TAF)',savepath=f'{save_dir}/groundwater_storage.png',fps=fps,factor=1)
# Groundwater Storage Duration
duration_plotter(file='groundwater_storage.csv',title='Monthly Groundwater Storage',ylabel='Storage (TAF)',savepath=f'{save_dir}/groundwater_storage_duration.png',fps=fps)
# Change in Groundwater Storage
ts_delta_stor_plotter(file='groundwater_storage.csv',title='Change in Groundwater Storage',ylabel='Storage Change (TAF)',savepath=f'{save_dir}/groundwater_storage_change.png',fps=fps)
# Annual Storage for each Basin
annual_average(file='groundwater_storage.csv',title='Annual Groundwater Storage',ylabel='Storage (TAF)',xlabel='Basin',savepath=f'{save_dir}/groundwater_storage_annual_average.png',fps=fps,kind='bar',factor=1,yscalelog=True)
# Monthly Groundwater Storage Violin Distribution
violin_plotter(file='groundwater_storage.csv',title='Monthly Groundwater Storage',ylabel='Storage (TAF)',savepath=f'{save_dir}/groundwater_storage_violin.png',fps=fps)

'''
Groundwater Pumping
'''
# Groundwater Pumping
ts_plotter(file='groundwater_pumping.csv',title='Annual Groundwater Pumping',ylabel='Flow (TAF/y)',savepath=f'{save_dir}/groundwater_pumping.png',fps=fps,factor=12)
# Groundwater Pumping Duration
duration_plotter(file='groundwater_pumping.csv',title='Monthly Groundwater Pumping',ylabel='Flow (TAF/m)',savepath=f'{save_dir}/groundwater_pumping_duration.png',fps=fps)
# Groundwater Monthly Pumping
monthly_average(file='groundwater_pumping.csv',title='Monthly Groundwater Pumping',ylabel='Flow (TAF/m)',savepath=f'{save_dir}/groundwater_pumping_monthly_average.png',fps=fps)
# Groundwater Pumping Violin Distribution
violin_plotter(file='groundwater_pumping.csv',title='Monthly Groundwater Pumping',ylabel='Flow (TAF/m)',savepath=f'{save_dir}/groundwater_pumping_violin.png',fps=fps)

'''
Ag Delivery
'''
print('Agricultural Delivery')
save_dir = 'plots/agricultural_deliveries'
os.makedirs(save_dir, exist_ok=True)

# Agricultural Delivery
ts_plotter(file='ag_delivery_total.csv',title='Annual Ag Delivery',ylabel='Delivery (TAF/y)',savepath=f'{save_dir}/ag_delivery.png',fps=fps,factor=12)
# Agricultural Delivery Duration
duration_plotter(file='ag_delivery_total.csv',title='Monthly Ag Delivery',ylabel='Delivery (TAF/m)',savepath=f'{save_dir}/ag_delivery_duration.png',fps=fps)
# Agricultural Monthly Delivery
monthly_average(file='ag_delivery_total.csv',title='Monthly Ag Delivery',ylabel='Delivery (TAF/m)',savepath=f'{save_dir}/ag_delivery_monthly_average.png',fps=fps)
# Annual Delivery for each Area
annual_average(file='ag_delivery_total.csv',title='Annual Ag Delivery',ylabel='Delivery (TAF/y)',xlabel='Demand Area',savepath=f'{save_dir}/ag_delivery_annual_average.png',fps=fps,kind='bar',factor=12,yscalelog=False)
# Monthly Delivery Violin Distribution
violin_plotter(file='ag_delivery_total.csv',title='Monthly Ag Delivery',ylabel='Delivery (TAF/m)',savepath=f'{save_dir}/ag_delivery_violin.png',fps=fps)

# Agricultural Delivery - Surface Water
ts_plotter(file='ag_delivery_sw.csv',title='Annual Ag Delivery - SW',ylabel='Delivery (TAF/y)',savepath=f'{save_dir}/ag_delivery_sw.png',fps=fps,factor=12)
# Agricultural Delivery Duration - Surface Water
duration_plotter(file='ag_delivery_sw.csv',title='Monthly Ag Delivery - SW',ylabel='Delivery (TAF/m)',savepath=f'{save_dir}/ag_delivery_duration_sw.png',fps=fps)
# Agricultural Monthly Delivery - Surface Water
monthly_average(file='ag_delivery_sw.csv',title='Monthly Ag Delivery - SW',ylabel='Delivery (TAF/m)',savepath=f'{save_dir}/ag_delivery_monthly_average_sw.png',fps=fps)

# Agricultural Delivery - Groundwater
ts_plotter(file='ag_delivery_gw.csv',title='Annual Ag Delivery - GW',ylabel='Delivery (TAF/y)',savepath=f'{save_dir}/ag_delivery_gw.png',fps=fps,factor=12)
# Agricultural Delivery Duration - Groundwater
duration_plotter(file='ag_delivery_gw.csv',title='Monthly Ag Delivery - GW',ylabel='Delivery (TAF/m)',savepath=f'{save_dir}/ag_delivery_duration_gw.png',fps=fps)
# Agricultural Monthly Delivery - Groundwater
monthly_average(file='ag_delivery_gw.csv',title='Monthly Ag Delivery - GW',ylabel='Delivery (TAF/m)',savepath=f'{save_dir}/ag_delivery_monthly_average_gw.png',fps=fps)

# Agricultural Scarcity
ts_plotter(file='ag_scarcity.csv',title='Annual Ag Scarcity',ylabel='Scarcity (TAF/y)',savepath=f'{save_dir}/ag_scarcity.png',fps=fps,factor=12)
# Agricultural Scarcity Duration
duration_plotter(file='ag_scarcity.csv',title='Monthly Ag Scarcity',ylabel='Scarcity (TAF/m)',savepath=f'{save_dir}/ag_scarcity_duration.png',fps=fps)
# Agricultural Monthly Scarcity
monthly_average(file='ag_scarcity.csv',title='Monthly Ag Scarcity',ylabel='Scarcity (TAF/m)',savepath=f'{save_dir}/ag_scarcity_monthly_average.png',fps=fps)
# Annual Scarcity for each Area
annual_average(file='ag_scarcity.csv',title='Annual Ag Scarcity',ylabel='Scarcity (TAF/y)',xlabel='Demand Area',savepath=f'{save_dir}/ag_scarcity_annual_average.png',fps=fps,kind='bar',factor=12,yscalelog=False)
# Monthly Scarcity Violin Distribution
violin_plotter(file='ag_scarcity.csv',title='Monthly Ag Scarcity',ylabel='Scarcity (TAF/m)',savepath=f'{save_dir}/ag_scarcity_violin.png',fps=fps)

# Percent Scarcity for each Area
annual_average(file='ag_scarcity_percent.csv',title='Annual Ag Scarcity',ylabel='Scarcity (% of Target)',xlabel='Demand Area',savepath=f'{save_dir}/ag_scarcity_annual_average_percent.png',fps=fps,kind='bar',factor=1,yscalelog=False)

'''
Urban Delivery
'''
print('Urban Delivery')
save_dir = 'plots/urban_deliveries'
os.makedirs(save_dir, exist_ok=True)

# Urban Delivery
ts_plotter(file='urban_delivery.csv',title='Annual Urban Delivery',ylabel='Delivery (TAF/y)',savepath=f'{save_dir}/urban_delivery.png',fps=fps,factor=12)
# Urban Delivery Duration
duration_plotter(file='urban_delivery.csv',title='Monthly Urban Delivery',ylabel='Delivery (TAF/m)',savepath=f'{save_dir}/urban_delivery_duration.png',fps=fps)
# Urban Monthly Delivery
monthly_average(file='urban_delivery.csv',title='Monthly Urban Delivery',ylabel='Delivery (TAF/m)',savepath=f'{save_dir}/urban_delivery_monthly_average.png',fps=fps)

# Urban Delivery - Surface Water
ts_plotter(file='urban_delivery_sw.csv',title='Annual Urban Delivery-SW',ylabel='Delivery (TAF/y)',savepath=f'{save_dir}/urban_delivery_sw.png',fps=fps,factor=12)
# Urban Delivery Duration - Surface Water
duration_plotter(file='urban_delivery_sw.csv',title='Monthly Urban Delivery-SW',ylabel='Delivery (TAF/m)',savepath=f'{save_dir}/urban_delivery_duration_sw.png',fps=fps)
# UrbanMonthly Delivery - Surface Water
monthly_average(file='urban_delivery_sw.csv',title='Monthly Urban Delivery-SW',ylabel='Delivery (TAF/m)',savepath=f'{save_dir}/urban_delivery_monthly_average_sw.png',fps=fps)

# Urban Delivery - Groundwater
ts_plotter(file='urban_delivery_gw.csv',title='Annual Urban Delivery-GW',ylabel='Delivery (TAF/y)',savepath=f'{save_dir}/urban_delivery_gw.png',fps=fps,factor=12)
# Urban Delivery Duration - Groundwater
duration_plotter(file='urban_delivery_gw.csv',title='Monthly Urban Delivery-GW',ylabel='Delivery (TAF/m)',savepath=f'{save_dir}/urban_delivery_duration_gw.png',fps=fps)
# Urban Monthly Delivery - Groundwater
monthly_average(file='urban_delivery_gw.csv',title='Monthly Avg. Urban Delivery-GW',ylabel='Delivery (TAF/m)',savepath=f'{save_dir}/urban_delivery_monthly_average_gw.png',fps=fps)

# Urban Delivery - Recycled Water
ts_plotter(file='urban_delivery_rc.csv',title='Annual Urban Delivery-RC',ylabel='Delivery (TAF/y)',savepath=f'{save_dir}/urban_delivery_rc.png',fps=fps,factor=12)
# Urban Delivery Duration - Recycled Water
duration_plotter(file='urban_delivery_rc.csv',title='Monthly Urban Delivery-RC',ylabel='Delivery (TAF/m)',savepath=f'{save_dir}/urban_delivery_duration_rc.png',fps=fps)
# Urban Monthly Delivery - Recycled Water
monthly_average(file='urban_delivery_rc.csv',title='Monthly Urban Delivery-RC',ylabel='Delivery (TAF/m)',savepath=f'{save_dir}/urban_delivery_monthly_average_rc.png',fps=fps)

# # Urban Scarcity
# ts_plotter(file='urban_scarcity.csv',title='Annual Urban Scarcity',ylabel='Scarcity (TAF/y)',savepath=f'{save_dir}/urban_scarcity.png',fps=fps,factor=12)
# # Agricultural Scarcity Duration
# duration_plotter(file='urban_scarcity.csv',title='Monthly Urban Scarcity',ylabel='Scarcity (TAF/m)',savepath=f'{save_dir}/urban_scarcity_duration.png',fps=fps)
# # Agricultural Monthly Scarcity
# monthly_average(file='urban_scarcity.csv',title='Monthly Urban Scarcity',ylabel='Scarcity (TAF/m)',savepath=f'{save_dir}/urban_scarcity_monthly_average.png',fps=fps)

'''
Delta Exports (CAA - DMC)
'''
print('Delta Exports')
save_dir = 'plots/delta_exports'
os.makedirs(save_dir, exist_ok=True)

# Delta Exports
ts_plotter(file='delta_exports.csv',title='Annual Delta Exports',ylabel='Flow (TAF/y)',savepath=f'{save_dir}/delta_exports.png',fps=fps,factor=12)
# Delta Exports Duration
duration_plotter(file='delta_exports.csv',title='Monthly Delta Exports',ylabel='Flow (TAF/m)',savepath=f'{save_dir}/delta_exports_duration.png',fps=fps)
# Delta Exports Monthly
monthly_average(file='delta_exports.csv',title='Monthly Delta Exports',ylabel='Flow (TAF/m)',savepath=f'{save_dir}/delta_exports_monthly_average.png',fps=fps)
# Monthly Delta Exports Violin Distribution
violin_plotter(file='delta_exports.csv',title='Monthly Delta Exports',ylabel='Flow (TAF/m)',savepath=f'{save_dir}/delta_exports_violin.png',fps=fps)


# Surplus Delta Outflow
ts_plotter(file='surplus_delta_outflow.csv',title='Annual Surplus Delta Outflow',ylabel='Flow (TAF/y)',savepath=f'{save_dir}/surplus_delta_outflow.png',fps=fps,factor=12)
# Surplus Delta Outflow Duration
duration_plotter(file='surplus_delta_outflow.csv',title='Monthly Surplus Delta Outflow',ylabel='Flow (TAF/m)',savepath=f'{save_dir}/surplus_delta_outflow_duration.png',fps=fps,yscalelog=True)
# Surplus Delta Outflow Monthly
monthly_average(file='surplus_delta_outflow.csv',title='Monthly Surplus Delta Outflow',ylabel='Flow (TAF/m)',savepath=f'{save_dir}/surplus_delta_outflow_monthly_average.png',fps=fps)

'''
Inflows (model inputs)
'''
print('Inflows')
save_dir = 'plots/inflow'
os.makedirs(save_dir, exist_ok=True)

# Rim Inflow
ts_plotter(file='rim_inflow.csv',title='Annual Rim Inflow',ylabel='Flow (TAF/y)',savepath=f'{save_dir}/rim_inflow.png',fps=fps,factor=12)
# Rim Inflow Duration
duration_plotter(file='rim_inflow.csv',title='Monthly Rim Inflow',ylabel='Flow (TAF/m)',savepath=f'{save_dir}/rim_inflow_duration.png',fps=fps,yscalelog=True)
# Rim Inflow Monthly
monthly_average(file='rim_inflow.csv',title='Monthly Avg. Rim Inflow',ylabel='Flow (TAF/m)',savepath=f'{save_dir}/rim_inflow_monthly_average.png',fps=fps,kind='line')

# Groundwater Inflow (Recharge)
ts_plotter(file='gw_inflow.csv',title='Annual Groundwater Inflow',ylabel='Flow (TAF/y)',savepath=f'{save_dir}/gw_inflow.png',fps=fps,factor=12)
# Groundwater Inflow Duration
duration_plotter(file='gw_inflow.csv',title='Monthly Groundwater Inflow',ylabel='Flow (TAF/m)',savepath=f'{save_dir}/gw_inflow_duration.png',fps=fps)
# Groundwater Inflow Monthly
monthly_average(file='gw_inflow.csv',title='Monthly Avg. Groundwater Inflow',ylabel='Flow (TAF/m)',savepath=f'{save_dir}/gw_inflow_monthly_average.png',fps=fps)

# fig,ax = plt.subplots(figsize=(5,4))
# data = pd.read_csv('ubt_ag_target_updated_02092026.csv', index_col=0, parse_dates=True)
# total_sum = data.sum(axis=1)
# monthly_avg = total_sum.groupby(total_sum.index.month).mean()
# plot_data = monthly_avg
# plot_data.index = monthly_avg.index
# plot_data.index.name = 'Month'
# plot_data.plot(kind='bar',ax=ax,rot=0,alpha=alpha,edgecolor='black')
# plt.xticks()
# plt.yticks()
# ax.patch.set(lw=2, ec='black')
# plt.xlabel('Month')
# plt.ylabel('Flow (TAF/m)')
# plt.title('Monthly Average Ag Target Demand',loc='left',fontweight='bold')
# plt.tight_layout()
# plt.savefig('plots/ag_target.png', transparent=False,dpi=300)
# plt.close(fig)

# # climate scenario
# scenarios = [
#                 'ACCESS-CM2',  # ssp370 does not exist
#                 'EC-Earth3-Veg',
#                 'FGOALS-g3',
#                 'GFDL-ESM4',
#                 'INM-CM5-0',
#                 'IPSL-CM6A-LR',
#                 'KACE-1-0-G',
#                 'MIROC6',
#                 'MPI-ESM1-2-HR',
#                 'MRI-ESM2-0',
#                 'TaiESM1' # ssp585 does not exist
#                 ]
# # ssp scenraio
# ssps = [
#         'ssp585',
#         'ssp370',
#         'ssp245',
#         ]

# # start and end year for averaging
# start = "2071-10-31"
# end   = "2100-09-30"

# # start and end year for averaging
# start_hist = "1981-10-31"
# end_hist   = "2010-09-30"

# # following scenarios do not exist in the database
# skip_pairs = {
#     ('ACCESS-CM2', 'ssp370'),
#     ('TaiESM1', 'ssp585')
# }

# # colors for ssps
# c = {'ssp245':'yellowgreen',
#       'ssp370':'cornflowerblue',
#       'ssp585':'tomato'}

# # statewide monthly average delivery
# fig,ax = plt.subplots(figsize=(5,4))
# for ssp in ssps:
#     ens = pd.DataFrame()
#     for scenario in scenarios:
#         if (scenario, ssp) in skip_pairs:
#             continue
#         # Read data
#         df_data = pd.read_csv(f"postprocess_network_{scenario}_{ssp}_no_overdraft_debug/ag_delivery_total.csv",index_col="date")
#         df = df_data.sum(axis=1)
#         sort = np.sort(df)[::-1]
#         exceedance = np.arange(1.,len(sort)+1) / len(sort)
#         # plt.plot(exceedence*100, sort,alpha=0.5,color=c[ssp])
#         ens[scenario] = sort
#         # plt.plot(0,0,alpha=0.4,color=c[ssp])
#         minimum = ens.min(axis=1)
#         maximum = ens.max(axis=1)
#     ens_avg = ens.median(axis=1)
#     plt.fill_between(exceedance*100, minimum, maximum,color=c[ssp],alpha=0.5,label=f'CMIP6 {ssp} range')
#     # plt.plot(0,0,alpha=0.4,label=f'CMIP6 {ssp} scenarios',color=c[ssp])
#     plt.plot(exceedance*100, ens_avg,color=c[ssp],label=ssp+' ensemble',linestyle='dotted',linewidth=4)

# # scenario = 'MPI-ESM1-2-HR'
# # ssp = 'ssp585'
# # df_data = pd.read_csv(f'postprocess_network_{scenario}_{ssp}_no_overdraft_debug/ag_delivery_total.csv',index_col='date')
# # df = df_data.sum(axis=1)
# # sort = np.sort(df)[::-1]
# # exceedence = np.arange(1.,len(sort)+1) / len(sort)
# # plt.plot(exceedence*100, sort,alpha=0.75,color='red',label=f'driest ({scenario} {ssp})')

# # scenario = 'KACE-1-0-G'
# # ssp = 'ssp585'
# # df_data = pd.read_csv(f'postprocess_network_{scenario}_{ssp}_no_overdraft_debug/ag_delivery_total.csv',index_col='date')
# # df = df_data.sum(axis=1)
# # sort = np.sort(df)[::-1]
# # exceedence = np.arange(1.,len(sort)+1) / len(sort)
# # plt.plot(exceedence*100, sort,alpha=0.75,color='cyan',label=f'wettest ({scenario} {ssp})')

# df_data = pd.read_csv('postprocess_network_1921_2015_basecase/ag_delivery_total.csv',index_col='date')
# df = df_data.sum(axis=1)
# sort = np.sort(df)[::-1]
# exceedence = np.arange(1.,len(sort)+1) / len(sort)
# plt.plot(exceedence*100, sort,alpha=0.75,color='blue',label=f'historical (with overdraft)')

# df_data = pd.read_csv('postprocess_network_1921_2015_basecase_no_overdraft_debug/ag_delivery_total.csv',index_col='date')
# df = df_data.sum(axis=1)
# sort = np.sort(df)[::-1]
# exceedence = np.arange(1.,len(sort)+1) / len(sort)
# plt.plot(exceedence*100, sort,alpha=0.75,color='magenta',label=f'historical (no overdraft)')

# # plt.grid()
# plt.legend(fontsize=10,ncol=1)
# plt.xticks(np.arange(0,101,10))
# plt.yticks()
# plt.ylim([0,None])
# ax.patch.set(lw=2, ec='black')
# plt.xlabel('Exceedance (%)')
# plt.ylabel('Delivery (TAF/month)')
# plt.title('a) Monthly Agricultural Water Delivery',loc='left',fontweight='bold',fontsize=13)
# plt.tight_layout()
# plt.savefig('plots/ag_delivery_duration.png', transparent=False,dpi=300)
# plt.close(fig)

# # statewide annual average delivery
# factor = 12
# fig,ax = plt.subplots(figsize=(5,4))
# for ssp in ssps:
#     ens = pd.DataFrame()
#     for scenario in scenarios:
#         if (scenario, ssp) in skip_pairs:
#             continue
#         # Read data
#         df_data = pd.read_csv(f"postprocess_network_{scenario}_{ssp}_no_overdraft_debug/ag_delivery_total.csv",index_col=0, parse_dates=True)
#         df = df_data.sum(axis=1)
#         df = df.groupby(df.index.year).mean()*factor
#         sort = np.sort(df)[::-1]
#         exceedance = np.arange(1.,len(sort)+1) / len(sort)
#         # plt.plot(exceedence*100, sort,alpha=0.5,color=c[ssp])
#         ens[scenario] = sort
#         # plt.plot(0,0,alpha=0.4,color=c[ssp])
#         minimum = ens.min(axis=1)
#         maximum = ens.max(axis=1)
#     ens_avg = ens.median(axis=1)
#     plt.fill_between(exceedance*100, minimum, maximum,color=c[ssp],alpha=0.5,label=f'CMIP6 {ssp} range')
#     # plt.plot(0,0,alpha=0.4,label=f'CMIP6 {ssp} scenarios',color=c[ssp])
#     plt.plot(exceedance*100, ens_avg,color=c[ssp],label=ssp+' ensemble',linestyle='dotted',linewidth=4)

# # scenario = 'MPI-ESM1-2-HR'
# # ssp = 'ssp585'
# # df_data = pd.read_csv(f'postprocess_network_{scenario}_{ssp}_no_overdraft_debug/ag_delivery_total.csv',index_col=0, parse_dates=True)
# # df = df_data.sum(axis=1)
# # df = df.groupby(df.index.year).mean()*factor
# # sort = np.sort(df)[::-1]
# # exceedence = np.arange(1.,len(sort)+1) / len(sort)
# # plt.plot(exceedence*100, sort,alpha=0.75,color='red',label=f'driest ({scenario} {ssp})')

# # scenario = 'KACE-1-0-G'
# # ssp = 'ssp585'
# # df_data = pd.read_csv(f'postprocess_network_{scenario}_{ssp}_no_overdraft_debug/ag_delivery_total.csv',index_col=0, parse_dates=True)
# # df = df_data.sum(axis=1)
# # df = df.groupby(df.index.year).mean()*factor
# # sort = np.sort(df)[::-1]
# # exceedence = np.arange(1.,len(sort)+1) / len(sort)
# # plt.plot(exceedence*100, sort,alpha=0.75,color='cyan',label=f'wettest ({scenario} {ssp})')

# df_data = pd.read_csv('postprocess_network_1921_2015_basecase/ag_delivery_total.csv',index_col=0, parse_dates=True)
# df = df_data.sum(axis=1)
# df = df.groupby(df.index.year).mean()*factor
# sort = np.sort(df)[::-1]
# exceedence = np.arange(1.,len(sort)+1) / len(sort)
# plt.plot(exceedence*100, sort,alpha=0.75,color='blue',label=f'historical (with overdraft)')

# df_data = pd.read_csv('postprocess_network_1921_2015_basecase_no_overdraft_debug/ag_delivery_total.csv',index_col=0, parse_dates=True)
# df = df_data.sum(axis=1)
# df = df.groupby(df.index.year).mean()*factor
# sort = np.sort(df)[::-1]
# exceedence = np.arange(1.,len(sort)+1) / len(sort)
# plt.plot(exceedence*100, sort,alpha=0.75,color='magenta',label=f'historical (no overdraft)')

# # plt.grid()
# plt.legend(fontsize=10,ncol=1)
# plt.xticks(np.arange(0,101,10))
# plt.yticks()
# plt.ylim([0,None])
# ax.patch.set(lw=2, ec='black')
# plt.xlabel('Exceedance (%)')
# plt.ylabel('Delivery (TAF/year)')
# plt.title('a) Annual Agricultural Water Delivery',loc='left',fontweight='bold',fontsize=13)
# plt.tight_layout()
# plt.savefig('plots/ag_delivery_duration_annual.png', transparent=False,dpi=300)
# plt.close(fig)

# # statewide average scarcity
# fig,ax = plt.subplots(figsize=(5,4))
# for ssp in ssps:
#     ens = pd.DataFrame()
#     for scenario in scenarios:
#         if (scenario, ssp) in skip_pairs:
#             continue
#         # Read data
#         df_data = pd.read_csv(f"postprocess_network_{scenario}_{ssp}_no_overdraft_debug/ag_scarcity_percent.csv",index_col="date")
#         df = df_data.mean(axis=1)
#         sort = np.sort(df)[::-1]
#         exceedance = np.arange(1.,len(sort)+1) / len(sort)
#         # plt.plot(exceedence*100, sort,alpha=0.5,color=c[ssp])
#         ens[scenario] = sort
#         # plt.plot(0,0,alpha=0.4,color=c[ssp])
#         minimum = ens.min(axis=1)
#         maximum = ens.max(axis=1)
#     ens_avg = ens.median(axis=1)
#     plt.fill_between(exceedance*100, minimum, maximum,color=c[ssp],alpha=0.5,label=f'CMIP6 {ssp} range')
#     # plt.plot(0,0,alpha=0.4,label=f'CMIP6 {ssp} scenarios',color=c[ssp])
#     plt.plot(exceedance*100, ens_avg,color=c[ssp],label=ssp+' ensemble',linestyle='dotted',linewidth=4)

# # scenario = 'MPI-ESM1-2-HR'
# # ssp = 'ssp585'
# # df_data = pd.read_csv(f'postprocess_network_{scenario}_{ssp}_no_overdraft_debug/ag_scarcity_percent.csv',index_col='date')
# # df = df_data.mean(axis=1)
# # sort = np.sort(df)[::-1]
# # exceedence = np.arange(1.,len(sort)+1) / len(sort)
# # plt.plot(exceedence*100, sort,alpha=0.75,color='red',label=f'driest ({scenario} {ssp})')

# # scenario = 'KACE-1-0-G'
# # ssp = 'ssp585'
# # df_data = pd.read_csv(f'postprocess_network_{scenario}_{ssp}_no_overdraft_debug/ag_scarcity_percent.csv',index_col='date')
# # df = df_data.mean(axis=1)
# # sort = np.sort(df)[::-1]
# # exceedence = np.arange(1.,len(sort)+1) / len(sort)
# # plt.plot(exceedence*100, sort,alpha=0.75,color='cyan',label=f'wettest ({scenario} {ssp})')

# df_data = pd.read_csv('postprocess_network_1921_2015_basecase/ag_scarcity_percent.csv',index_col='date')
# df = df_data.mean(axis=1)
# sort = np.sort(df)[::-1]
# exceedence = np.arange(1.,len(sort)+1) / len(sort)
# plt.plot(exceedence*100, sort,alpha=0.75,color='blue',label=f'historical (with overdraft)')

# df_data = pd.read_csv('postprocess_network_1921_2015_basecase_no_overdraft_debug/ag_scarcity_percent.csv',index_col='date')
# df = df_data.mean(axis=1)
# sort = np.sort(df)[::-1]
# exceedence = np.arange(1.,len(sort)+1) / len(sort)
# plt.plot(exceedence*100, sort,alpha=0.75,color='magenta',label=f'historical (no overdraft)')


# # plt.grid()
# # plt.legend(fontsize=9,ncol=2)
# plt.xticks(np.arange(0,101,10))
# plt.yticks()
# # plt.xlim([1,12])
# plt.ylim([0,50])
# ax.patch.set(lw=2, ec='black')
# plt.xlabel('Exceedance (%)')
# plt.ylabel('Scarcity (% of Target Demand)')
# plt.title('b) Monthly Agricultural Water Scarcity',loc='left',fontweight='bold',fontsize=13)
# plt.tight_layout()
# plt.savefig('plots/ag_scarcity_percent_duration.png', transparent=False,dpi=300)
# plt.close(fig)

# # annual average scarcity table
# annual_data = pd.DataFrame()
# for ssp in ssps:
#     for scenario in scenarios:
#         if (scenario, ssp) in skip_pairs:
#             continue
#         # Read data
#         df_data = pd.read_csv(f"postprocess_network_{scenario}_{ssp}_no_overdraft_debug/ag_scarcity_percent.csv",index_col="date")
#         total_annual = df_data.mean(axis=0)
#         annual_data[f'{scenario}_{ssp}'] = total_annual
# df_data = pd.read_csv('postprocess_network_1921_2015_basecase/ag_scarcity_percent.csv',index_col='date')
# total_annual = df_data.mean(axis=0)
# annual_data['historical_basecase'] = total_annual

# df_data = pd.read_csv('postprocess_network_1921_2015_basecase_no_overdraft_debug/ag_scarcity_percent.csv',index_col='date')
# total_annual = df_data.mean(axis=0)
# annual_data['historical_no_overdraft'] = total_annual

# annual_data.index = total_annual.index
# annual_data.index.name = 'Annual Average (% of target)'
# annual_data.to_csv('plots/annual_scarcity_percent_of_target.csv')
        
        