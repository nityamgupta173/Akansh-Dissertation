"""Download the selected RIL press releases and keep their text (data/deals/press_releases/*.txt)."""
import os, re, subprocess, tempfile
import pandas as pd

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "..", "data", "deals", "press_releases")
os.makedirs(OUT, exist_ok=True)
sel = pd.read_csv(os.path.join(HERE, "..", "data", "deals", "selected_press_releases.csv"), parse_dates=["date"])
tmp = tempfile.mkdtemp()
for i, r in sel.iterrows():
    slug = re.sub(r"[^A-Za-z0-9]+", "_", r.title)[:60].strip("_")
    txt = os.path.join(OUT, f"{r.date.date()}_{slug}.txt")
    if os.path.exists(txt):
        continue
    url = r.url.replace("https://rilstaticasset.akamaized.net/", "https://www.ril.com/")
    pdf = os.path.join(tmp, "x.pdf")
    subprocess.run(["curl", "-sL", "-m", "60", "-A", "Mozilla/5.0", url, "-o", pdf])
    subprocess.run(["pdftotext", "-layout", pdf, txt], stderr=subprocess.DEVNULL)
    n = len(open(txt, errors="ignore").read().split()) if os.path.exists(txt) else 0
    print(r.date.date(), n, "words", slug[:50])
