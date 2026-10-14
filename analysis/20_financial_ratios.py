"""Build a consistent financial panel (Screener.in + annual reports) and compute ratios.

Outputs: results/ratios_panel.csv (company x fiscal year)
"""
import json, os, re
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
FIN = os.path.join(HERE, "..", "data", "financials")
RAW = os.path.join(HERE, "..", "data", "raw", "screener")
RES = os.path.join(HERE, "..", "results")

COMPANIES = ["RELIANCE_consolidated", "NETWORK18_consolidated", "DEN_consolidated", "HATHWAY_consolidated",
             "ALOKINDS_consolidated", "JUSTDIAL", "SWSOLAR_consolidated"]


def fy_of(col):
    m = re.match(r"Mar (\d{4})$", str(col).strip())
    return int(m.group(1)) if m else None


def num(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return np.nan
    try:
        return float(str(x).replace(",", "").replace("%", ""))
    except ValueError:
        return np.nan


def screener_panel(name):
    t = pd.read_csv(os.path.join(FIN, name + ".csv"), index_col=0)
    sch = json.load(open(os.path.join(RAW, name + "_schedules.json")))
    rows = {}
    for col in t.columns:
        fy = fy_of(col)
        if fy is None:
            continue
        g = lambda k: t.loc[k, col] if k in t.index else np.nan
        def s(sec, parent, item):
            d = (sch.get(f"{sec}:{parent}") or {}).get(item, {})
            return num(d.get(col.strip()))
        rows[fy] = {
            "sales": g("profit-loss:Sales"), "operating_profit": g("profit-loss:Operating Profit"),
            "other_income": g("profit-loss:Other Income"), "interest": g("profit-loss:Interest"),
            "depreciation": g("profit-loss:Depreciation"), "pbt": g("profit-loss:Profit before tax"),
            "net_profit": g("profit-loss:Net Profit"),
            "profit_owners": s("profit-loss", "Net Profit", "Profit for EPS"),
            "equity_capital": g("balance-sheet:Equity Capital"), "reserves": g("balance-sheet:Reserves"),
            "borrowings": g("balance-sheet:Borrowings"),
            "short_term_borrowings": s("balance-sheet", "Borrowings", "Short term Borrowings"),
            "total_assets": g("balance-sheet:Total Assets"), "fixed_assets": g("balance-sheet:Fixed Assets"),
            "cwip": g("balance-sheet:CWIP"), "investments": g("balance-sheet:Investments"),
            "inventories": s("balance-sheet", "Other Assets", "Inventories"),
            "receivables": s("balance-sheet", "Other Assets", "Trade receivables"),
            "cash": s("balance-sheet", "Other Assets", "Cash Equivalents"),
            "loans_advances": s("balance-sheet", "Other Assets", "Loans n Advances"),
            "trade_payables": s("balance-sheet", "Other Liabilities", "Trade Payables"),
            "minority_interest": s("balance-sheet", "Other Liabilities", "Non controlling int"),
            "cfo": g("cash-flow:Cash from Operating Activity"),
            "capex": -s("cash-flow", "Cash from Investing Activity", "Fixed assets purchased"),
            "source": "Screener.in",
        }
    df = pd.DataFrame(rows).T
    df.index.name = "fy"
    return df


panels = []
manual = pd.read_csv(os.path.join(FIN, "manual", "pre_2015_from_annual_reports.csv"))
for c in COMPANIES:
    p = screener_panel(c).reset_index()
    p["company"] = c
    m = manual[manual.company == c].copy()
    if len(m):
        m["operating_profit"] = m.pbt + m.interest + m.depreciation - m.other_income
        p = pd.concat([m, p[~p.fy.isin(m.fy)]], ignore_index=True)
    panels.append(p)
P = pd.concat(panels, ignore_index=True).sort_values(["company", "fy"])
num_cols = [c for c in P.columns if c not in ("company", "source", "fy")]
P[num_cols] = P[num_cols].apply(pd.to_numeric, errors="coerce")
P["fy"] = P.fy.astype(int)

eq = P.equity_capital + P.reserves
eq_pos = eq.where(eq > 0)          # ratios on equity are not meaningful when net worth is negative
ebit = P.pbt + P.interest
po = P.profit_owners.fillna(P.net_profit)
P["OPM_%"] = 100 * P.operating_profit / P.sales
P["NPM_%"] = 100 * P.net_profit / P.sales
P["ROE_%"] = 100 * po / eq_pos
P["ROCE_%"] = 100 * ebit / (eq + P.borrowings).where(lambda x: x > 0)
P["ROA_%"] = 100 * P.net_profit / P.total_assets
P["Liquidity_ratio"] = (P.inventories.fillna(0) + P.receivables.fillna(0) + P.cash + P.loans_advances.fillna(0)) / \
                       (P.trade_payables + P.short_term_borrowings.fillna(0))
P["Cash_to_assets_%"] = 100 * P.cash / P.total_assets
P["Debt_equity"] = P.borrowings / eq_pos
P["Interest_cover"] = ebit / P.interest.replace(0, np.nan)
P["Asset_turnover"] = P.sales / P.total_assets
P["Fixed_asset_turnover"] = P.sales / P.fixed_assets
P["Net_debt_cr"] = P.borrowings - P.cash
P.to_csv(os.path.join(RES, "ratios_panel.csv"), index=False)
show = ["company", "fy", "sales", "OPM_%", "NPM_%", "ROE_%", "ROCE_%", "Debt_equity", "Liquidity_ratio", "Asset_turnover"]
print(P[show].round(2).to_string())
