"""Event study of RIL's M&A announcements (market model, Nifty 50 benchmark).

Outputs (results/): event_study_ril_events.csv, event_study_groups.csv, event_study_targets.csv,
event_study_caar_path.csv, event_study_robustness.csv, event_study_cross_section.csv
"""
import os
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")
os.makedirs(RES, exist_ok=True)

EST = (-250, -30)          # estimation window (trading days relative to event day)
MIN_FRAC = 0.8           # minimum share of the estimation window with valid returns
WINDOWS = [(0, 0), (-1, 1), (-2, 2), (-5, 5), (-10, 10), (-10, -2), (2, 10)]


def load_returns(ticker):
    f = os.path.join(DATA, "prices", ticker.replace("^", "") + ".csv")
    p = pd.read_csv(f, parse_dates=["date"]).set_index("date")["adjclose"]
    p = p[p > 0]
    return np.log(p).diff().dropna()


MKT = load_returns("NSEI")


def event_ar(ticker, event_day, est=EST, model="market"):
    r = load_returns(ticker)
    df = pd.concat([r.rename("r"), MKT.rename("m")], axis=1, join="inner").dropna()
    # drop zero-volume style stale days (|r|==0 and |m|>0 is fine; keep simple)
    idx = df.index
    ed = pd.Timestamp(event_day)
    if ed not in idx:
        later = idx[idx >= ed]
        if len(later) == 0:
            return None
        ed = later[0]
    t0 = idx.get_loc(ed)
    rel = np.arange(len(idx)) - t0
    df = df.assign(rel=rel)
    e = df[(df.rel >= est[0]) & (df.rel <= est[1])]
    if len(e) < MIN_FRAC * (est[1] - est[0] + 1):
        return None
    if model == "market":
        beta, alpha = np.polyfit(e.m, e.r, 1)
    else:  # market-adjusted
        beta, alpha = 1.0, 0.0
    resid = e.r - (alpha + beta * e.m)
    s = resid.std(ddof=2)
    w = df[(df.rel >= -10) & (df.rel <= 10)].copy()
    w["ar"] = w.r - (alpha + beta * w.m)
    return {"alpha": alpha, "beta": beta, "sigma": s, "n_est": len(e), "ar": w.set_index("rel")["ar"],
            "event_trading_day": ed}


def car_stats(res, a, b):
    ar = res["ar"].loc[a:b]
    L = b - a + 1
    car = ar.sum()
    scar = car / (res["sigma"] * np.sqrt(L))
    return car, scar


def group_tests(cars, scars, n_est):
    cars, scars = np.asarray(cars), np.asarray(scars)
    n = len(cars)
    out = {"N": n, "CAAR_%": 100 * cars.mean(), "median_%": 100 * np.median(cars),
           "pct_positive": 100 * (cars > 0).mean()}
    if n > 1:
        t = cars.mean() / (cars.std(ddof=1) / np.sqrt(n))
        out["t_cs"] = t
        out["p_cs"] = 2 * stats.t.sf(abs(t), n - 1)
        T = np.mean(n_est)
        z = scars.sum() / np.sqrt(n * (T - 2) / (T - 4))
        out["patell_z"] = z
        out["p_patell"] = 2 * stats.norm.sf(abs(z))
        tb = scars.mean() / (scars.std(ddof=1) / np.sqrt(n))
        out["bmp_t"] = tb
        out["p_bmp"] = 2 * stats.t.sf(abs(tb), n - 1)
        if n >= 6:
            out["p_wilcoxon"] = stats.wilcoxon(cars).pvalue
        out["p_sign"] = stats.binomtest(int((cars > 0).sum()), n, 0.5).pvalue
    return out


def run_events(events, ticker_col=None, est=EST, model="market"):
    rows, paths = [], []
    for _, ev in events.iterrows():
        tk = ev[ticker_col] if ticker_col else "RELIANCE.NS"
        res = event_ar(tk, ev.event_day, est, model)
        if res is None:
            print("skip", ev.id)
            continue
        row = {"id": ev.id, "ticker": tk, "event_day": res["event_trading_day"].date(),
               "alpha": res["alpha"], "beta": res["beta"], "sigma_%": 100 * res["sigma"], "n_est": res["n_est"]}
        for a, b in WINDOWS:
            car, scar = car_stats(res, a, b)
            row[f"CAR({a},{b})_%"] = 100 * car
            row[f"t({a},{b})"] = scar
            row[f"_scar({a},{b})"] = scar
        rows.append(row)
        paths.append(res["ar"].rename(ev.id))
    return pd.DataFrame(rows), pd.concat(paths, axis=1)


def summarise(df, label):
    out = []
    for a, b in WINDOWS:
        g = group_tests(df[f"CAR({a},{b})_%"] / 100, df[f"_scar({a},{b})"], df.n_est)
        out.append({"sample": label, "window": f"({a},{b})", **g})
    return out


if __name__ == "__main__":
    deals = pd.read_csv(os.path.join(DATA, "deals", "deals_master.csv"))
    ev, path = run_events(deals)
    ev = deals[["id", "group", "deal", "cluster", "bower_type", "ansoff", "relatedness", "mode", "motive",
                "value_inr_cr", "confounded"]].merge(ev, on="id")

    # relative size: deal value / RIL market value 5 trading days before the event
    px = pd.read_csv(os.path.join(DATA, "prices", "RELIANCE.NS.csv"), parse_dates=["date"]).set_index("date")["close"]
    def mcap(d):
        d = pd.Timestamp(d)
        p = px[px.index < d].iloc[-5]
        shares = 1268.7 if d < pd.Timestamp("2020-05-20") else 1353.2   # crore shares, current bonus basis
        return p * shares
    ev["ril_mcap_cr"] = ev.event_day.apply(mcap)
    ev["rel_size_%"] = 100 * ev.value_inr_cr / ev.ril_mcap_cr
    ev.drop(columns=[c for c in ev.columns if c.startswith("_")]).to_csv(
        os.path.join(RES, "event_study_ril_events.csv"), index=False)

    groups = []
    A = ev[ev.group == "A"]
    groups += summarise(A, "A: Acquisitions & strategic investments (all)")
    groups += summarise(A[A.confounded == 0], "A: excluding confounded events")
    groups += summarise(A[A.value_inr_cr >= 1000], "A: deals >= Rs 1,000 crore")
    for c in ["Media & Entertainment", "Digital & Technology", "Retail & Consumer", "New Energy & Materials"]:
        groups += summarise(A[A.cluster == c], f"A: {c}")
    groups += summarise(ev[ev.group == "B"], "B: Inbound strategic stake sales")
    groups += summarise(ev[ev.group == "C"], "C: Deal reversals")
    pd.DataFrame(groups).to_csv(os.path.join(RES, "event_study_groups.csv"), index=False)

    # CAAR path by group
    cp = pd.DataFrame({g: path[ev[ev.group == g].id].mean(axis=1).cumsum() * 100 for g in ["A", "B"]})
    cp.index.name = "rel_day"
    cp.to_csv(os.path.join(RES, "event_study_caar_path.csv"))
    path.to_csv(os.path.join(RES, "event_study_ar_paths.csv"))

    # robustness: market-adjusted model and shorter estimation window
    rob = []
    for label, kw in [("Market model, est. (-250,-30)", {}),
                      ("Market-adjusted returns", {"model": "adjusted"}),
                      ("Market model, est. (-150,-11)", {"est": (-150, -11)})]:
        e2, _ = run_events(deals[deals.group == "A"], **kw)
        for a, b in [(-1, 1), (-5, 5)]:
            g = group_tests(e2[f"CAR({a},{b})_%"] / 100, e2[f"_scar({a},{b})"], e2.n_est)
            rob.append({"specification": label, "window": f"({a},{b})", **g})
    pd.DataFrame(rob).to_csv(os.path.join(RES, "event_study_robustness.csv"), index=False)

    # cross-section of CAR(-1,+1) for group A
    cs = []
    x = A["CAR(-1,1)_%"]
    for col in ["cluster", "bower_type", "relatedness"]:
        grp = [g["CAR(-1,1)_%"].values for _, g in A.groupby(A[col].str.split(" \\(").str[0]) if len(g) > 1]
        kw = stats.kruskal(*grp) if len(grp) > 1 else None
        cs.append({"test": f"Kruskal-Wallis CAR(-1,+1) by {col}", "stat": kw.statistic, "p": kw.pvalue})
    sub = A.dropna(subset=["rel_size_%"])
    rho = stats.spearmanr(sub["rel_size_%"], sub["CAR(-1,1)_%"])
    cs.append({"test": "Spearman CAR(-1,+1) vs relative deal size", "stat": rho.statistic, "p": rho.pvalue,
               "N": len(sub)})
    pd.DataFrame(cs).to_csv(os.path.join(RES, "event_study_cross_section.csv"), index=False)

    # target firms
    tg = pd.read_csv(os.path.join(DATA, "deals", "target_events.csv"))
    te, tpath = run_events(tg, ticker_col="ticker")
    te = tg[["id", "company", "event"]].merge(te, on="id")
    te.drop(columns=[c for c in te.columns if c.startswith("_")]).to_csv(
        os.path.join(RES, "event_study_targets.csv"), index=False)
    tpath.to_csv(os.path.join(RES, "event_study_target_ar_paths.csv"))
    tgt = summarise(te[te.id.isin(["T02", "T03", "T04", "T05", "T06", "T07"])], "Targets: six acquired listed companies")
    pd.DataFrame(tgt).to_csv(os.path.join(RES, "event_study_target_groups.csv"), index=False)
    print("done")
