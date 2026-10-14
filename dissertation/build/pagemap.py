"""Read a rendered PDF and map headings, tables and figures to printed page labels -> pagemap.json."""
import json, re, subprocess, sys

pdf, reg_file, out = sys.argv[1], sys.argv[2], sys.argv[3]
reg = json.load(open(reg_file))
n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))
pages = []
for i in range(1, n + 1):
    t = subprocess.run(["pdftotext", "-layout", "-f", str(i), "-l", str(i), pdf, "-"], capture_output=True, text=True).stdout
    lines = [l.strip() for l in t.splitlines() if l.strip()]
    m = next((re.match(r"^([ivxlc]+|\d+)\s*\|\s*P\s*a\s*g\s*e", l) for l in reversed(lines) if re.match(r"^([ivxlc]+|\d+)\s*\|", l)), None)
    pages.append({"label": m.group(1) if m else "", "lines": lines})
norm = lambda s: re.sub(r"\s+", " ", s).strip().lower()
# skip TOC and list pages when searching for captions and headings
start_main = next(i for i, p in enumerate(pages) if any(norm(l) == "list of abbreviations" for l in p["lines"]))
toc_start = next(i for i, p in enumerate(pages) if any(norm(l) == "table of contents" for l in p["lines"]))
pm = {}
for h in reg["headings"]:
    key = norm(h["text"])[:45]
    rng = range(0, n)
    for i in rng:
        if toc_start <= i < start_main and key not in ("table of contents", "list of tables", "list of figures"):
            continue
        full = norm(h["text"])
        hit = (any(norm(l) == full for l in pages[i]["lines"]) if h["level"] == 1
               else any(norm(l).startswith(key) and "...." not in l for l in pages[i]["lines"]))
        if hit:
            pm[h["text"]] = pages[i]["label"]; break
for t in reg["tables"] + reg["figures"]:
    for i in range(start_main, n):
        if any(norm(l).startswith(norm(t["label"]) + ":") for l in pages[i]["lines"]):
            pm[t["label"]] = pages[i]["label"]; break
missing = [h["text"] for h in reg["headings"] if h["text"] not in pm] + [t["label"] for t in reg["tables"] + reg["figures"] if t["label"] not in pm]
json.dump(pm, open(out, "w"), indent=1)
print(len(pm), "mapped; missing:", missing)
