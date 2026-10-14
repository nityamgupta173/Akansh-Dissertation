"""Convert Yahoo Finance chart JSON downloads to tidy CSV files."""
import json, glob, os
import pandas as pd

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "prices")
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "prices")
os.makedirs(OUT, exist_ok=True)

for f in sorted(glob.glob(os.path.join(RAW, "*.json"))):
    r = json.load(open(f))["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    df = pd.DataFrame({
        "date": pd.to_datetime(r["timestamp"], unit="s").tz_localize("UTC").tz_convert("Asia/Kolkata").date,
        "open": q["open"], "high": q["high"], "low": q["low"], "close": q["close"],
        "volume": q["volume"],
        "adjclose": r["indicators"]["adjclose"][0]["adjclose"],
    }).dropna(subset=["close"]).drop_duplicates("date", keep="last")
    name = os.path.basename(f).replace(".json", "")
    df.to_csv(os.path.join(OUT, name + ".csv"), index=False)
    print(name, len(df), df.date.min(), df.date.max())
