"""Figures for the dissertation (PNG, 300 dpi) -> figures/."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
DATA = os.path.join(HERE, "..", "data")
FIG = os.path.join(HERE, "..", "figures")
os.makedirs(FIG, exist_ok=True)

C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]          # validated categorical slots 1-4 (light)
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "legend.frameon": False, "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
    "axes.titlesize": 10, "axes.titleweight": "bold", "axes.titlecolor": INK,
})
MARK = ["o", "s", "^", "D"]


def save(fig, name):
    fig.savefig(os.path.join(FIG, name), facecolor="white")
    plt.close(fig)


# Figure 4.1: number of deals per fiscal year by cluster (stacked bars with 1px surface gaps)
x = pd.read_csv(os.path.join(RES, "deals_fy_x_cluster.csv"), index_col=0)
order = ["Media & Entertainment", "Digital & Technology", "Retail & Consumer", "New Energy & Materials"]
x = x.reindex(columns=order, fill_value=0).reindex(range(2012, 2027), fill_value=0)
fig, ax = plt.subplots(figsize=(6.3, 3.0))
bottom = np.zeros(len(x))
for i, c in enumerate(order):
    ax.bar(x.index, x[c], bottom=bottom, color=C[i], width=0.7, edgecolor="white", linewidth=1, label=c)
    bottom += x[c].values
for xi, tot in zip(x.index, bottom):
    if tot:
        ax.text(xi, tot + 0.1, int(tot), ha="center", va="bottom", fontsize=8, color=INK)
ax.set_xticks(x.index, [f"FY{str(y)[2:]}" for y in x.index], fontsize=7.5, rotation=45)
ax.set_ylabel("Announcements")
ax.set_ylim(0, bottom.max() + 1.2)
ax.grid(axis="x", visible=False)
ax.legend(ncol=2, loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=8)
save(fig, "fig4_1_deals_by_year.png")

# Figure 4.2: share of segment EBIT
s = pd.read_csv(os.path.join(DATA, "financials", "manual", "ril_segments.csv"))
p = s.pivot(index="fy", columns="segment", values="segment_ebit_cr")
share = p.div(p.sum(axis=1), axis=0) * 100
share["Consumer businesses (Digital + Retail)"] = share[["Digital Services", "Retail"]].sum(axis=1, min_count=1)
fig, ax = plt.subplots(figsize=(6.3, 3.0))
series = [("O2C", "O2C (refining & petrochemicals)"), ("Digital Services", "Digital Services (Jio)"),
          ("Retail", "Retail"), ("Consumer businesses (Digital + Retail)", "Digital + Retail")]
nudge = {0: 5, 1: -5, 2: 0, 3: 0}            # keep the FY26 end labels of O2C and Digital apart
for i, (col, lab) in enumerate(series):
    y = share[col]
    ls = "--" if i == 3 else "-"
    ax.plot(y.index, y, color=C[i], lw=1.8, ls=ls, marker=MARK[i], ms=4, label=lab)
    ax.annotate(f"{y.dropna().iloc[-1]:.0f}%", (y.dropna().index[-1], y.dropna().iloc[-1]),
                xytext=(6, nudge[i]), textcoords="offset points", va="center", fontsize=8, color=INK)
ax.set_xticks(share.index, [f"FY{str(y)[2:]}" for y in share.index])
ax.set_ylabel("Share of segment EBIT (%)")
ax.set_ylim(-5, 105)
ax.legend(loc="center left", bbox_to_anchor=(0.0, 0.62), fontsize=8)
save(fig, "fig4_2_segment_mix.png")

# Figure 4.3: annual-report theme intensity
a = pd.read_csv(os.path.join(RES, "content_annual_reports.csv"))
a = a.set_index("fy").reindex(range(a.fy.min(), a.fy.max() + 1)).reset_index()   # gap for FY15-FY16, no line across it
fig, ax = plt.subplots(figsize=(6.3, 3.0))
th = ["Digital ecosystem & platform", "Consumer reach & new commerce", "Green energy transition", "Acquisition mentions"]
for i, t in enumerate(th):
    ax.plot(a.fy, a[t], color=C[i], lw=1.8, marker=MARK[i], ms=4, label=t)
ax.set_xticks(a.fy, [f"FY{str(y)[2:]}" for y in a.fy], fontsize=7.5, rotation=45)
ax.set_ylabel("Mentions per 10,000 words")
ax.legend(fontsize=8, loc="upper left")
ax.text(0.99, 0.02, "FY15-FY16 reports not included", transform=ax.transAxes, ha="right", fontsize=7, color=INK2)
save(fig, "fig4_3_annual_report_themes.png")

# Figure 4.4: CAAR path
cp = pd.read_csv(os.path.join(RES, "event_study_caar_path.csv"), index_col=0)
fig, ax = plt.subplots(figsize=(6.3, 3.0))
for i, (g, lab) in enumerate([("A", "A: acquisitions & strategic investments (N=30)"),
                              ("B", "B: inbound strategic stake sales (N=5)")]):
    ax.plot(cp.index, cp[g], color=C[i], lw=1.8, marker=MARK[i], ms=3.5, label=lab)
    ax.annotate(f"{cp[g].iloc[-1]:+.1f}%", (cp.index[-1], cp[g].iloc[-1]), xytext=(6, 0),
                textcoords="offset points", va="center", fontsize=8, color=INK)
ax.axvline(0, color=INK2, lw=0.8, ls=":")
ax.axhline(0, color=INK2, lw=0.8)
ax.set_xlabel("Trading days relative to announcement (day 0)")
ax.set_ylabel("CAAR (%)")
ax.set_xticks(range(-10, 11, 2))
ax.legend(fontsize=8, loc="upper left", frameon=True, facecolor="white", edgecolor="white", framealpha=1)
save(fig, "fig4_4_caar_path.png")

# Figure 4.5: CAR(-1,+1) per acquisition, sorted, coloured by cluster
e = pd.read_csv(os.path.join(RES, "event_study_ril_events.csv"))
A = e[e.group == "A"].copy()
short = {"A01": "Network18/TV18 funding (2012)", "A02": "Network18 control (2014)", "A03": "Kemrock assets (2017)",
         "A04": "RCom wireless assets (2017)", "A05": "Eros 5% (2018)", "A06": "Saavn (2018)", "A07": "Embibe (2018)",
         "A08": "Radisys (2018)", "A09": "Den & Hathway (2018)", "A10": "Alok Industries (2019)",
         "A11": "Haptik (2019)", "A12": "Hamleys (2019)", "A13": "Netmeds (2020)", "A14": "Future Group (2020)",
         "A15": "Urban Ladder (2020)", "A16": "skyTran (2021)", "A17": "Just Dial (2021)", "A18": "Ambri (2021)",
         "A19": "REC Solar + S&W (2021)", "A20": "Faradion (2022)", "A21": "Addverb (2022)", "A22": "Glance (2022)",
         "A23": "Lithium Werks (2022)", "A24": "Clovia (2022)", "A25": "SenseHawk (2022)", "A26": "Metro C&C (2022)",
         "A27": "Sosyo JV (2023)", "A28": "Superdry IP (2023)", "A29": "Viacom18-Star JV (2024)",
         "A30": "Kelvinator (2025)"}
A["label"] = A.id.map(short)
A = A.sort_values("CAR(-1,1)_%")
col = {c: C[i] for i, c in enumerate(order)}
fig, ax = plt.subplots(figsize=(6.3, 6.4))
ax.barh(A.label, A["CAR(-1,1)_%"], color=A.cluster.map(col), height=0.7, edgecolor="white", linewidth=1)
for yi, (v, t) in enumerate(zip(A["CAR(-1,1)_%"], A["t(-1,1)"])):
    star = "*" if abs(t) >= 1.96 else ""
    ax.text(v + (0.15 if v >= 0 else -0.15), yi, f"{v:+.1f}{star}", va="center",
            ha="left" if v >= 0 else "right", fontsize=7, color=INK)
ax.axvline(0, color=INK2, lw=0.8)
ax.set_xlabel("CAR(-1,+1), %   (* |t| >= 1.96)")
ax.grid(axis="y", visible=False)
ax.tick_params(axis="y", labelsize=7.5)
ax.set_xlim(A["CAR(-1,1)_%"].min() - 1.5, A["CAR(-1,1)_%"].max() + 1.5)
handles = [plt.Rectangle((0, 0), 1, 1, color=col[c]) for c in order]
ax.legend(handles, order, fontsize=7.5, loc="lower right")
save(fig, "fig4_5_car_by_deal.png")

# Figure 4.6: RIL ratios over time (small multiples, one measure per panel)
P = pd.read_csv(os.path.join(RES, "ratios_panel.csv"))
R = P[P.company == "RELIANCE_consolidated"].set_index("fy")
ev_years = [2015, 2019, 2020, 2021, 2022, 2023]
fig, axes = plt.subplots(2, 2, figsize=(6.3, 4.4), sharex=True)
for ax, (col_, lab) in zip(axes.flat, [("OPM_%", "Operating profit margin (%)"), ("ROE_%", "Return on equity (%)"),
                                       ("ROCE_%", "Return on capital employed (%)"), ("Debt_equity", "Debt-equity (x)")]):
    for yv in ev_years:
        ax.axvspan(yv - 0.4, yv + 0.4, color="#f1f0ec", lw=0)
    ax.plot(R.index, R[col_], color=C[0], lw=1.8, marker="o", ms=3.5)
    ax.set_title(lab, loc="left", fontsize=9)
    ax.set_xticks(range(2012, 2027, 2), [f"FY{str(y)[2:]}" for y in range(2012, 2027, 2)])
    ax.tick_params(labelsize=7.5)
fig.text(0.01, -0.01, "Shaded bars: fiscal years in which major acquisitions were completed (FY15, FY19-FY23).",
         fontsize=7.5, color=INK2)
fig.tight_layout()
save(fig, "fig4_6_ril_ratios.png")

# Figure 4.7: targets pre vs post (dumbbells) for OPM and debt-equity
T = pd.read_csv(os.path.join(RES, "prepost_targets_by_company.csv"))
fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.8), sharey=True)
names = T.company.str.replace(" Media & Investments", "").str.replace(" Renewable Energy", "").str.replace(" Cable & Datacom", "")
for ax, (r, lab) in zip(axes, [("OPM_%", "Operating margin (%)"), ("Debt_equity", "Debt-equity (x)")]):
    for yi, (a0, a1) in enumerate(zip(T[f"pre_{r}"], T[f"post_{r}"])):
        if np.isnan(a0) or np.isnan(a1):
            ax.text(0.5, yi, "n.m. (negative net worth)", transform=ax.get_yaxis_transform(), ha="center",
                    va="center", fontsize=7, color=INK2)
            continue
        ax.plot([a0, a1], [yi, yi], color="#c3c2b7", lw=1.5, zorder=1)
        ax.scatter([a0], [yi], color=C[1], s=28, zorder=2, label="3-yr pre" if yi == 0 else None, edgecolor="white", linewidth=1)
        ax.scatter([a1], [yi], color=C[0], s=28, zorder=2, marker="s", label="3-yr post" if yi == 0 else None, edgecolor="white", linewidth=1)
    ax.set_title(lab, loc="left", fontsize=9)
    ax.set_yticks(range(len(T)), names)
    ax.grid(axis="y", visible=False)
    ax.tick_params(labelsize=7.5)
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, fontsize=7.5, loc="upper center", ncol=2, bbox_to_anchor=(0.55, 1.06))
fig.tight_layout()
save(fig, "fig4_7_targets_prepost.png")

# Figure 4.8: target firms' CAR path
tp = pd.read_csv(os.path.join(RES, "event_study_target_ar_paths.csv"), index_col=0)
six = ["T02", "T03", "T04", "T05", "T06", "T07"]
fig, ax = plt.subplots(figsize=(6.3, 3.0))
avg = tp[six].mean(axis=1).cumsum() * 100
ax.plot(avg.index, avg, color=C[0], lw=2, marker="o", ms=3.5, label="Average of six acquired companies")
for t, lab, i in [("T02", "Network18 (2014)", 1), ("T06", "Just Dial (2021)", 2)]:
    y = tp[t].cumsum() * 100
    ax.plot(y.index, y, color=C[i], lw=1.4, ls="--", marker=MARK[i], ms=3, label=lab)
for ser in [avg]:
    ax.annotate(f"{ser.iloc[-1]:+.1f}%", (ser.index[-1], ser.iloc[-1]), xytext=(6, 0), textcoords="offset points",
                va="center", fontsize=8, color=INK)
ax.axvline(0, color=INK2, lw=0.8, ls=":")
ax.axhline(0, color=INK2, lw=0.8)
ax.set_xticks(range(-10, 11, 2))
ax.set_xlabel("Trading days relative to announcement (day 0)")
ax.set_ylabel("Cumulative abnormal return (%)")
ax.legend(fontsize=8, loc="upper left")
save(fig, "fig4_8_target_car.png")
print(sorted(os.listdir(FIG)))
