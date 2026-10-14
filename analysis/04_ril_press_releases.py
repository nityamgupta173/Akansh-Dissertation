"""Index RIL's press-release archive (title, date, PDF link) from ril.com/news-media/press-releases."""
import os, re, subprocess
import pandas as pd
from bs4 import BeautifulSoup

rows = []
for p in range(0, 60):
    html = subprocess.run(["curl", "-sL", "-m", "30", "-A", "Mozilla/5.0",
                           f"https://www.ril.com/news-media/press-releases?page={p}"],
                          capture_output=True, text=True).stdout
    soup = BeautifulSoup(html, "html.parser")
    boxes = soup.select("div.press-txt")
    if not boxes:
        break
    for b in boxes:
        a = b.find("a")
        pub = b.find("div", class_="publish")
        rows.append({"title": a.get_text(" ", strip=True) if a else "",
                     "published": pub.get_text(" ", strip=True).split("|")[-1].strip() if pub else "",
                     "url": a["href"] if a else ""})
df = pd.DataFrame(rows).drop_duplicates()
df["date"] = pd.to_datetime(df["published"], format="%d %b, %Y", errors="coerce")
out = os.path.join(os.path.dirname(__file__), "..", "data", "deals", "ril_press_releases.csv")
os.makedirs(os.path.dirname(out), exist_ok=True)
df.sort_values("date").to_csv(out, index=False)
print(len(df), df.date.min(), df.date.max())
