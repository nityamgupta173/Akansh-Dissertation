"""Parse annual tables (P&L, balance sheet, cash flow, ratios) from saved Screener.in pages."""
import glob, io, os, re
import pandas as pd
from bs4 import BeautifulSoup

BASE = os.path.join(os.path.dirname(__file__), "..", "data")
OUT = os.path.join(BASE, "financials")
os.makedirs(OUT, exist_ok=True)


def num(x):
    if pd.isna(x):
        return None
    x = str(x).replace(",", "").replace("%", "").strip()
    try:
        return float(x)
    except ValueError:
        return None


for f in sorted(glob.glob(os.path.join(BASE, "raw", "screener", "*.html"))):
    soup = BeautifulSoup(open(f).read(), "html.parser")
    frames = []
    for sec in ["profit-loss", "balance-sheet", "cash-flow", "ratios"]:
        node = soup.find("section", id=sec)
        if node is None or node.find("table") is None:
            continue
        df = pd.read_html(io.StringIO(str(node.find("table"))))[0]
        df = df.rename(columns={df.columns[0]: "item"})
        df["item"] = df["item"].astype(str).str.replace("+", "", regex=False).str.strip()
        df = df.set_index("item")
        df = df[[c for c in df.columns if re.match(r"(Mar|Dec|Jun|Sep) \d{4}", str(c))]]
        df = df.map(num)
        df.index = [f"{sec}:{i}" for i in df.index]
        frames.append(df)
    out = pd.concat(frames)
    name = os.path.basename(f).replace(".html", "")
    out.to_csv(os.path.join(OUT, name + ".csv"))
    print(name, list(out.columns)[0], "->", list(out.columns)[-1], out.shape)
