import csv
import os
import datetime
from collections import defaultdict
import pandas as pd

def save_dict_as_csv(data, filename, mode="w"):
    """
    Write nested dict {col: {time: value}} to CSV.

    Given nested dict `data`, write to CSV file
    where rows are timesteps and columns are links/nodes as appropriate.
    
    :param data: (dict) Nested dictionary of results data
    :param filename: (string) Output CSV filename
    :param mode: (string) file writing mode, 'w' for write, 'a' for append
      in particular the annual optimization uses 'a' to append results each year.
    :returns: nothing, but writes the output CSV file.
    """

    if not data:
        return

    node_keys = sorted(data.keys())
    time_keys = sorted({t for k in data for t in data[k]})

    with open(filename, mode, newline="") as f:
        writer = csv.writer(f)
        if mode == "w":
            writer.writerow(["date"] + node_keys)
        for t in time_keys:
            row = [t] + [round(data[k].get(t, 0.0),3) for k in node_keys]
            writer.writerow(row)


def dict_get(D, k1, k2, default=0.0):
    """
    Custom retrieval from nested dictionary.
    Get D[k1][k2] if it exists, otherwise default.
    """
    return D.get(k1, {}).get(k2, default)


def dict_insert(D, k1, k2, v, collision_rule=None):
    """Insert into nested dict with collision handling.
    Custom insertion into nested dictionary.
    Assign D[k1][k2] = v if those keys do not exist yet.
    If the keys do exist, follow instructions for collision_rule
    """
    if k1 not in D:
        D[k1] = {k2: v}
        return

    if k2 not in D[k1]:
        D[k1][k2] = v
        return

    if collision_rule == "sum":
        D[k1][k2] += v
    elif collision_rule == "first":
        pass
    elif collision_rule == "last":
        D[k1][k2] = v
    else:
        raise ValueError(f"Duplicate key [{k1}][{k2}] with no rule")


def postprocess(df, model, resultdir=None, annual=False):
    """Convert model outputs into structured CSV files.

    Postprocess model results into timeseries CSV files.

    :param df: (dataframe) network links data
    :param model: (CALVIN object) model object, post-optimization
    :param resultdir: (string) directory to place CSV file results
    :param annual: (boolean) whether to run annual optimization or not
    :returns EOP_storage: (dict) end-of-period storage, only when 
      running annual optimization. Otherwise returns nothing, but writes files.
    """
    # start with empty dicts -- this is
    # what we want to output (in separate files):
    # flows (F), storages (S), duals (D), evap (E), shortage vol (SV) and cost (SC)
    F = defaultdict(dict)
    S = defaultdict(dict)
    E = defaultdict(dict)
    SV = defaultdict(dict)
    SC = defaultdict(dict)
    D_up = defaultdict(dict)
    D_lo = defaultdict(dict)
    D_node = defaultdict(dict)
    EOP_storage = {}

    links = df.values
    nodes = pd.unique(df[["i", "j"]].values.ravel())
    demand_nodes = pd.read_csv("calvin/data/demand_nodes.csv", index_col=0)

    for link in links:
        # get values from JSON results. If they don't exist, default is 0.0.
        s = tuple(link[:3])

        v = model.X[s].value if s in model.X else 0.0
        d1 = model.dual[model.limit_lower[s]] if s in model.limit_lower else 0.0
        d2 = model.dual[model.limit_upper[s]] if s in model.limit_upper else 0.0

        # now figure out what keys to save it in the dictionaries
        if "." in link[0] and "." in link[1]:
            n1, t1 = link[0].split(".")
            n2, _ = link[1].split(".")
            is_storage = n1 == n2
            amplitude = float(link[4]) if is_storage else None

        elif "." in link[0] and link[1] == "FINAL":
            n1, t1 = link[0].split(".")
            is_storage = True
            amplitude = 1
            EOP_storage[n1] = v

        else:
            continue

        # sum over piecewise components
        if is_storage:
            evap = (1 - amplitude) * v / amplitude if amplitude else 0.0
            dict_insert(S, n1, t1, v, "sum")
            dict_insert(E, n1, t1, evap, "sum")
            key = n1
        else:
            key = f"{n1}-{n2}"
            dict_insert(F, key, t1, v, "sum")

            # Check for urban or ag demands
            if key in demand_nodes.index:
                ub = float(link[6])
                unit_cost = float(link[3])
                shortage = max(ub - v, 0.0)

                dict_insert(SV, key, t1, shortage, "sum")
                dict_insert(SC, key, t1, -unit_cost * shortage, "sum")

        dict_insert(D_up, key, t1, d1, "last")
        dict_insert(D_lo, key, t1, d2, "first")

    # get dual values for nodes (mass balance)
    for node in nodes:
        if "." in node:
            n, t = node.split(".")
            d = model.dual[model.flow[node]] if node in model.flow else 0.0
            dict_insert(D_node, n, t, d)

    # Output directory
    if not resultdir:
        if annual:
            raise RuntimeError("resultdir required for annual run")
        resultdir = f"results-{datetime.datetime.utcnow():%Y-%m-%dT%H-%M-%SZ}"

    os.makedirs(resultdir, exist_ok=True)
    mode = "a" if (annual and os.path.exists(resultdir)) else "w"
    
    # remove GW columns from Evaporation
    E = {k: v for k, v in E.items() if not k.startswith("GW")}

    outputs = [
        (F, "flow"),
        (S, "storage"),
        (D_up, "dual_upper"),
        (D_lo, "dual_lower"),
        (D_node, "dual_node"),
        (E, "evaporation"),
        (SV,'shortage_volume'),
        (SC,'shortage_cost')
    ]

    for data, name in outputs:
        save_dict_as_csv(data, os.path.join(resultdir, f"{name}.csv"), mode)


def aggregate_regions(fp):
    """
    Read the results CSV files and aggregate results by region (optional).

    :param fp: (string) directory where output files are written.
    :returns: nothing, but overwrites the results files with new
      columns added for regional aggregations.
    """

    sc = pd.read_csv(f"{fp}/shortage_cost.csv", index_col=0, parse_dates=True)
    sv = pd.read_csv(f"{fp}/shortage_volume.csv", index_col=0, parse_dates=True)
    flow = pd.read_csv(f"{fp}/flow.csv", index_col=0, parse_dates=True)

    demand_nodes = pd.read_csv("calvin/data/demand_nodes.csv", index_col=0)
    portfolio = pd.read_csv("calvin/data/portfolio.csv", index_col=0)

    for (region, t), group in demand_nodes.groupby(["region", "type"]):
        sc[f"{region}_{t}"] = sc[group.index].sum(axis=1)
        sv[f"{region}_{t}"] = sv[group.index].sum(axis=1)

    for (region, supply, t), group in portfolio.groupby(
        ["region", "supplytype", "type"]
    ):
        flow[f"{region}_{supply}_{t}"] = flow[group.index].sum(axis=1)

    sc.to_csv(f"{fp}/shortage_cost.csv")
    sv.to_csv(f"{fp}/shortage_volume.csv")
    flow.to_csv(f"{fp}/flow.csv")