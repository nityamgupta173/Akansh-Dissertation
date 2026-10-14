"""Format result tables for the Word document -> results/doc_tables.json (lists of string rows)."""
import json, os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
DATA = os.path.join(HERE, "..", "data")
out = {}


def f(x, d=2, sign=False, pct=False):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "–"
    s = f"{x:+.{d}f}" if sign else f"{x:.{d}f}"
    return s.replace("-", "−") + ("%" if pct else "")


def p(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "–"
    return "<0.001" if x < 0.001 else f"{x:.3f}"


deals = pd.read_csv(os.path.join(DATA, "deals", "deals_master.csv"))
deals[deals.select_dtypes("object").columns] = deals.select_dtypes("object").fillna("")
ev = pd.read_csv(os.path.join(RES, "event_study_ril_events.csv"))
A = deals[deals.group == "A"]

# deal list
out["deal_list"] = [[r.id, pd.Timestamp(r.announce_date).strftime("%d-%b-%Y"), r.deal, r.cluster, r.stake_or_form,
                     r.value_reported] for r in A.itertuples()]
out["deal_list_bc"] = [[r.id, pd.Timestamp(r.announce_date).strftime("%d-%b-%Y"), r.deal, r.stake_or_form,
                        r.value_reported, r.note] for r in deals[deals.group != "A"].itertuples()]
# strategy matrix
out["strategy_matrix"] = [[r.id, r.deal, r.mode, r.relatedness, r.ansoff, r.bower_type, r.motive] for r in A.itertuples()]

bc = pd.read_csv(os.path.join(RES, "deals_by_cluster.csv"), index_col=0)
out["by_cluster"] = [[i, f"{int(r.deals)}", f"{int(r.with_value)}", f"{r.value_cr:,.0f}", f"{r.median_cr:,.0f}"]
                     for i, r in bc.iterrows()]
cx = pd.read_csv(os.path.join(RES, "deals_cluster_x_bower.csv"), index_col=0)
cx["Total"] = cx.sum(axis=1)
cx.loc["Total"] = cx.sum()
out["cluster_x_bower_cols"] = ["Cluster"] + list(cx.columns)
out["cluster_x_bower"] = [[i] + [str(int(v)) for v in r.values] for i, r in cx.iterrows()]
for col in ["ansoff", "mode", "motive"]:
    t = pd.read_csv(os.path.join(RES, f"deals_by_{col}.csv"))
    out[f"by_{col}"] = [[r[0], str(r[1])] for r in t.values]

cap = pd.read_csv(os.path.join(RES, "acquisitions_vs_capex.csv"), index_col=0)
out["acq_capex"] = [[f"FY{str(i)[2:]}", f"{r.announced_acquisitions_cr:,.0f}" if r.announced_acquisitions_cr > 0 else "–",
                     f"{r.inbound_stake_sales_cr:,.0f}" if r.inbound_stake_sales_cr > 0 else "–",
                     f"{r.capex_cr:,.0f}", f(r["acq_as_%_capex"], 1) if r.announced_acquisitions_cr > 0 else "–"]
                    for i, r in cap.iterrows()]
tot = cap.sum()
out["acq_capex"].append(["Total", f"{tot.announced_acquisitions_cr:,.0f}", f"{tot.inbound_stake_sales_cr:,.0f}",
                         f"{tot.capex_cr:,.0f}", f(100 * tot.announced_acquisitions_cr / tot.capex_cr, 1)])

cc = pd.read_csv(os.path.join(RES, "content_by_cluster.csv"), index_col=0)
out["content_cluster_cols"] = ["Theme"] + list(cc.index)
out["content_cluster"] = [[t] + [f(v, 1) for v in cc[t].values] for t in cc.columns]
ar = pd.read_csv(os.path.join(RES, "content_annual_reports.csv"))
out["content_ar"] = [[f"FY{str(r.fy)[2:]}", f"{r.words:,.0f}"] + [f(r[c], 1) for c in
                     ["Digital ecosystem & platform", "Consumer reach & new commerce", "Content & media",
                      "Green energy transition", "Partnership & capital", "Acquisition mentions"]] for _, r in ar.iterrows()]

# event study groups
g = pd.read_csv(os.path.join(RES, "event_study_groups.csv"))
rows = []
for s in g["sample"].unique():
    sub = g[g["sample"] == s].set_index("window")
    for w in ["(0,0)", "(-1,1)", "(-5,5)", "(-10,10)"]:
        r = sub.loc[w]
        rows.append([s if w == "(0,0)" else "", w.replace("-", "−"), str(int(r.N)), f(r["CAAR_%"], 2, True),
                     f(r.pct_positive, 0), f(r.t_cs, 2), p(r.p_cs), f(r.patell_z, 2), p(r.p_patell), p(r.p_bmp),
                     p(r.get("p_wilcoxon", np.nan))])
out["es_groups"] = rows
rb = pd.read_csv(os.path.join(RES, "event_study_robustness.csv"))
out["es_robust"] = [[r.specification, r.window.replace("-", "−"), f(r["CAAR_%"], 2, True), f(r.t_cs, 2), p(r.p_cs),
                     p(r.p_patell), p(r.p_bmp), p(r.p_wilcoxon)] for _, r in rb.iterrows()]
cs = pd.read_csv(os.path.join(RES, "event_study_cross_section.csv"))
out["es_cross"] = [[r.test, f(r.stat, 3), p(r.p)] for _, r in cs.iterrows()]
# deal-level
out["es_events"] = [[r.id, r.deal[:48], str(r.event_day), f(r.beta, 2), f(r["CAR(0,0)_%"], 2, True), f(r["t(0,0)"], 2),
                     f(r["CAR(-1,1)_%"], 2, True), f(r["t(-1,1)"], 2), f(r["CAR(-5,5)_%"], 2, True),
                     f(r["CAR(-10,10)_%"], 2, True), f(r["rel_size_%"], 2)] for _, r in ev.iterrows()]
te = pd.read_csv(os.path.join(RES, "event_study_targets.csv"))
out["es_targets"] = [[r.company, r.event[:55], str(r.event_day), f(r["CAR(0,0)_%"], 2, True), f(r["t(0,0)"], 2),
                      f(r["CAR(-1,1)_%"], 2, True), f(r["t(-1,1)"], 2), f(r["CAR(-10,-2)_%"], 2, True),
                      f(r["CAR(-10,10)_%"], 2, True)] for _, r in te.iterrows()]
tg = pd.read_csv(os.path.join(RES, "event_study_target_groups.csv"))
out["es_target_groups"] = [[r.window.replace("-", "−"), f(r["CAAR_%"], 2, True), f(r.pct_positive, 0), f(r.t_cs, 2),
                            p(r.p_cs), f(r.patell_z, 2), p(r.p_patell), p(r.p_wilcoxon)] for _, r in tg.iterrows()]

# pre/post
lab = {"OPM_%": "Operating profit margin (%)", "NPM_%": "Net profit margin (%)", "ROE_%": "Return on equity (%)",
       "ROCE_%": "Return on capital employed (%)", "ROA_%": "Return on assets (%)",
       "Liquidity_ratio": "Liquidity ratio (x)", "Cash_to_assets_%": "Cash to total assets (%)",
       "Debt_equity": "Debt-equity (x)", "Interest_cover": "Interest coverage (x)", "Asset_turnover": "Asset turnover (x)",
       "Fixed_asset_turnover": "Fixed-asset turnover (x)", "Sales_growth_%": "Sales growth (%)"}
for key, fn in [("pp_targets", "prepost_targets_tests.csv"), ("pp_ril", "prepost_ril_tests.csv")]:
    t = pd.read_csv(os.path.join(RES, fn))
    out[key] = [[r.category, lab[r.ratio], str(int(r.N)), f(r.mean_pre), f(r.mean_post), f(r.median_pre), f(r.median_post),
                 f(r.t, 2), p(r.p_t), p(r.p_wilcoxon)] for _, r in t.iterrows()]
T = pd.read_csv(os.path.join(RES, "prepost_targets_by_company.csv"))
out["pp_by_company"] = []
for _, r in T.iterrows():
    for k in ["OPM_%", "NPM_%", "ROCE_%", "Debt_equity", "Asset_turnover", "Sales_growth_%"]:
        out["pp_by_company"].append([r.company if k == "OPM_%" else "", lab[k], f(r[f"pre_{k}"]), f(r[f"post_{k}"]),
                                     f(r[f"post_{k}"] - r[f"pre_{k}"], 2, True)])
R = pd.read_csv(os.path.join(RES, "prepost_ril_by_eventyear.csv"))
out["pp_ril_years"] = [[f"FY{str(r.event_fy)[2:]}", r.deals, f(r["pre_OPM_%"]), f(r["post_OPM_%"]), f(r["pre_ROE_%"]),
                        f(r["post_ROE_%"]), f(r["pre_ROCE_%"]), f(r["post_ROCE_%"]), f(r.pre_Debt_equity),
                        f(r.post_Debt_equity)] for _, r in R.iterrows()]

# RIL panel and target panels (appendix)
P = pd.read_csv(os.path.join(RES, "ratios_panel.csv"))
Rp = P[P.company == "RELIANCE_consolidated"]
out["ril_panel"] = [[f"FY{str(r.fy)[2:]}", f"{r.sales:,.0f}", f"{r.operating_profit:,.0f}", f"{r.net_profit:,.0f}",
                     f(r["OPM_%"], 1), f(r["NPM_%"], 1), f(r["ROE_%"], 1), f(r["ROCE_%"], 1), f(r.Debt_equity),
                     f(r.Interest_cover, 1), f(r.Asset_turnover), f(r.Liquidity_ratio)] for _, r in Rp.iterrows()]
names = {"NETWORK18_consolidated": "Network18", "DEN_consolidated": "Den Networks", "HATHWAY_consolidated": "Hathway",
         "ALOKINDS_consolidated": "Alok Industries", "JUSTDIAL": "Just Dial", "SWSOLAR_consolidated": "Sterling & Wilson"}
out["target_panel"] = []
for c, n in names.items():
    sub = P[(P.company == c) & P.sales.notna()]
    for _, r in sub.iterrows():
        out["target_panel"].append([n, f"FY{str(r.fy)[2:]}", f"{r.sales:,.0f}", f(r["OPM_%"], 1), f(r["NPM_%"], 1),
                                    f(r["ROCE_%"], 1), f(r.Debt_equity), f(r.Asset_turnover)])

# segments
s = pd.read_csv(os.path.join(DATA, "financials", "manual", "ril_segments.csv"))
rev = s.pivot(index="fy", columns="segment", values="revenue_cr")
eb = s.pivot(index="fy", columns="segment", values="segment_ebit_cr")
share = eb.div(eb.sum(axis=1), axis=0) * 100
out["segments"] = [[f"FY{str(y)[2:]}", f"{rev.loc[y, 'Retail']:,.0f}", f(100 * eb.loc[y, 'Retail'] / rev.loc[y, 'Retail'], 1),
                    f"{rev.loc[y, 'Digital Services']:,.0f}" if not np.isnan(rev.loc[y, 'Digital Services']) else "–",
                    f(100 * eb.loc[y, 'Digital Services'] / rev.loc[y, 'Digital Services'], 1),
                    f(100 * eb.loc[y, 'O2C'] / rev.loc[y, 'O2C'], 1), f(share.loc[y, 'O2C'], 1),
                    f(share.loc[y, ['Retail', 'Digital Services']].sum(), 1)] for y in rev.index]
json.dump(out, open(os.path.join(RES, "doc_tables.json"), "w"), indent=0, ensure_ascii=False)
print({k: len(v) for k, v in out.items()})
