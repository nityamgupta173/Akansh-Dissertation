"""Descriptive statistics of the deal sample and inorganic spend relative to RIL's capital expenditure."""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
d = pd.read_csv(os.path.join(DATA, "deals", "deals_master.csv"), parse_dates=["announce_date"])
d["fy"] = d.announce_date.dt.year + (d.announce_date.dt.month >= 4).astype(int)
A = d[d.group == "A"]

by_cluster = A.groupby("cluster").agg(deals=("id", "count"), with_value=("value_inr_cr", "count"),
                                      value_cr=("value_inr_cr", "sum"), median_cr=("value_inr_cr", "median"))
by_cluster.loc["Total"] = [len(A), A.value_inr_cr.count(), A.value_inr_cr.sum(), A.value_inr_cr.median()]
by_cluster.to_csv(os.path.join(RES, "deals_by_cluster.csv"))

for col in ["bower_type", "ansoff", "mode", "motive"]:
    A.groupby(col).id.count().sort_values(ascending=False).to_csv(os.path.join(RES, f"deals_by_{col}.csv"))
pd.crosstab(A.cluster, A.bower_type).to_csv(os.path.join(RES, "deals_cluster_x_bower.csv"))
pd.crosstab(A.fy, A.cluster).to_csv(os.path.join(RES, "deals_fy_x_cluster.csv"))

# announced acquisition value vs capital expenditure, by fiscal year
P = pd.read_csv(os.path.join(RES, "ratios_panel.csv"))
capex = P[P.company == "RELIANCE_consolidated"].set_index("fy").capex
val = A.groupby("fy").value_inr_cr.sum()
inbound = d[d.group == "B"].groupby("fy").value_inr_cr.sum()
s = pd.DataFrame({"announced_acquisitions_cr": val, "inbound_stake_sales_cr": inbound, "capex_cr": capex}).loc[2015:2026]
s["acq_as_%_capex"] = 100 * s.announced_acquisitions_cr / s.capex_cr
s.to_csv(os.path.join(RES, "acquisitions_vs_capex.csv"))
print(by_cluster.round(0)); print(s.round(1)); print(s.sum().round(0))
print(pd.crosstab(A.cluster, A.bower_type))
