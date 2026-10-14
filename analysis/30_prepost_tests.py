"""Pre- vs post-acquisition financial performance: paired t-tests and Wilcoxon signed-rank tests.

Level 1 - acquired companies (six listed targets): mean of years e-3..e-1 vs e+1..e+3, where e is the
fiscal year in which RIL obtained control. Level 2 - RIL (acquirer): the same comparison around each
fiscal year in which a major acquisition was completed.
Outputs: results/prepost_targets_by_company.csv, results/prepost_targets_tests.csv,
results/prepost_ril_by_eventyear.csv, results/prepost_ril_tests.csv
"""
import os
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
P = pd.read_csv(os.path.join(RES, "ratios_panel.csv"))
P = P.sort_values(["company", "fy"])
P["Sales_growth_%"] = P.groupby("company").sales.pct_change(fill_method=None) * 100

RATIOS = {
    "Profitability": ["OPM_%", "NPM_%", "ROE_%", "ROCE_%", "ROA_%"],
    "Liquidity": ["Liquidity_ratio", "Cash_to_assets_%"],
    "Solvency": ["Debt_equity", "Interest_cover"],
    "Efficiency": ["Asset_turnover", "Fixed_asset_turnover"],
    "Growth": ["Sales_growth_%"],
}
ALL = [r for v in RATIOS.values() for r in v]
CAT = {r: k for k, v in RATIOS.items() for r in v}

TARGETS = {  # company -> (label, fiscal year control obtained)
    "NETWORK18_consolidated": ("Network18 Media & Investments", 2015),
    "DEN_consolidated": ("Den Networks", 2019),
    "HATHWAY_consolidated": ("Hathway Cable & Datacom", 2019),
    "ALOKINDS_consolidated": ("Alok Industries", 2020),
    "JUSTDIAL": ("Just Dial", 2022),
    "SWSOLAR_consolidated": ("Sterling and Wilson Renewable Energy", 2022),
}
RIL_EVENT_YEARS = {
    2015: "Network18 (control, Jul 2014)",
    2019: "Den, Hathway, Saavn, Embibe, Radisys",
    2020: "Alok, Haptik, Hamleys",
    2021: "Netmeds, Urban Ladder; Jio/RRVL stake sales",
    2022: "Just Dial, REC Solar, S&W, Faradion, Clovia, Addverb",
    2023: "Lithium Werks, SenseHawk, Metro Cash & Carry",
}


def window_means(df, e, k=3):
    pre = df[(df.fy >= e - k) & (df.fy <= e - 1)]
    post = df[(df.fy >= e + 1) & (df.fy <= e + k)]
    return pre[ALL].mean(), post[ALL].mean(), len(pre), len(post)


def paired_tests(rows, label_col):
    out = []
    for r in ALL:
        d = rows[[f"pre_{r}", f"post_{r}"]].dropna()
        n = len(d)
        rec = {"ratio": r, "category": CAT[r], "N": n,
               "mean_pre": d.iloc[:, 0].mean(), "mean_post": d.iloc[:, 1].mean(),
               "median_pre": d.iloc[:, 0].median(), "median_post": d.iloc[:, 1].median()}
        if n >= 3:
            diff = d.iloc[:, 1] - d.iloc[:, 0]
            t = stats.ttest_rel(d.iloc[:, 1], d.iloc[:, 0])
            rec.update({"mean_diff": diff.mean(), "t": t.statistic, "p_t": t.pvalue,
                        "improved_n": int((diff > 0).sum())})
            try:
                rec["p_wilcoxon"] = stats.wilcoxon(diff).pvalue
            except ValueError:
                rec["p_wilcoxon"] = np.nan
        out.append(rec)
    return pd.DataFrame(out)


# Level 1: targets
rows = []
for c, (label, e) in TARGETS.items():
    pre, post, npre, npost = window_means(P[P.company == c], e)
    row = {"company": label, "event_fy": e, "years_pre": npre, "years_post": npost}
    row.update({f"pre_{k}": v for k, v in pre.items()})
    row.update({f"post_{k}": v for k, v in post.items()})
    rows.append(row)
T = pd.DataFrame(rows)
T.to_csv(os.path.join(RES, "prepost_targets_by_company.csv"), index=False)
paired_tests(T, "company").to_csv(os.path.join(RES, "prepost_targets_tests.csv"), index=False)

# Level 2: RIL
R = P[P.company == "RELIANCE_consolidated"]
rows = []
for e, lab in RIL_EVENT_YEARS.items():
    pre, post, npre, npost = window_means(R, e)
    row = {"event_fy": e, "deals": lab, "years_pre": npre, "years_post": npost}
    row.update({f"pre_{k}": v for k, v in pre.items()})
    row.update({f"post_{k}": v for k, v in post.items()})
    rows.append(row)
RR = pd.DataFrame(rows)
RR.to_csv(os.path.join(RES, "prepost_ril_by_eventyear.csv"), index=False)
paired_tests(RR, "event_fy").to_csv(os.path.join(RES, "prepost_ril_tests.csv"), index=False)

pd.set_option("display.width", 220)
print(pd.read_csv(os.path.join(RES, "prepost_targets_tests.csv")).round(3).to_string())
print(pd.read_csv(os.path.join(RES, "prepost_ril_tests.csv")).round(3).to_string())
