"""Download line-item breakdowns ("schedules") behind Screener's condensed statements."""
import json, os, re, subprocess, time, urllib.parse

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "screener")
PARENTS = {
    "profit-loss": ["Sales", "Expenses", "Other Income", "Net Profit"],
    "balance-sheet": ["Borrowings", "Other Liabilities", "Fixed Assets", "Other Assets"],
    "cash-flow": ["Cash from Operating Activity", "Cash from Investing Activity", "Cash from Financing Activity"],
}
for page in sorted(os.listdir(BASE)):
    if not page.endswith(".html"):
        continue
    html = open(os.path.join(BASE, page)).read()
    cid = re.search(r'data-company-id="(\d+)"', html).group(1)
    consolidated = "true" if "consolidated" in page else ""
    out = {}
    for sec, parents in PARENTS.items():
        for p in parents:
            url = (f"https://www.screener.in/api/company/{cid}/schedules/?parent={urllib.parse.quote(p)}"
                   f"&section={sec}&consolidated={consolidated}")
            r = subprocess.run(["curl", "-s", "-m", "30", "-A", "Mozilla/5.0", url], capture_output=True, text=True)
            try:
                out[f"{sec}:{p}"] = json.loads(r.stdout)
            except json.JSONDecodeError:
                out[f"{sec}:{p}"] = None
            time.sleep(0.4)
    json.dump(out, open(os.path.join(BASE, page.replace(".html", "_schedules.json")), "w"), indent=1)
    print(page, cid, sum(v is not None for v in out.values()), "/", len(out))
