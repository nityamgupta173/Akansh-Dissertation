"""Dictionary-based content analysis of RIL's stated strategic intent.

(1) Deal press releases (data/deals/press_releases/*.txt): theme intensity per 1,000 words by business cluster.
(2) Annual reports (text extracted from PDFs; directory given as argv[1]): theme intensity per 10,000 words by year.
Outputs: results/content_press_releases.csv, results/content_by_cluster.csv, results/content_annual_reports.csv
"""
import glob, os, re, sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
RES = os.path.join(HERE, "..", "results")

THEMES = {
    "Digital ecosystem & platform": r"\becosystems?\b|\bplatforms?\b|\bdigital\b|\bconnectivity\b|\bbroadband\b",
    "Content & media": r"\bcontent\b|\bentertainment\b|\bmusic\b|\bmedia\b|\bstreaming\b|\bsports\b|\bchannels?\b",
    "Technology & capability": r"\btechnolog(y|ies|ical)\b|\bartificial intelligence\b|\bAI\b|\bR&D\b|\bpatent(s|ed)?\b|\binnovati(on|ve)\b|\bIP\b|\b5G\b|\bengineering\b",
    "Consumer reach & new commerce": r"\bconsumers?\b|\bcustomers?\b|\bomni-?channel\b|\bstores?\b|\bcommerce\b|\bmerchants?\b|\bkiranas?\b|\bMSMEs?\b",
    "Scale & leadership": r"\blargest\b|\bleader(s|ship)?\b|\bleading\b|\bscale\b|\bmarket share\b|\bnationwide\b|\bpan[- ]India\b",
    "Brands & portfolio": r"\bbrands?\b|\bheritage\b|\biconic\b|\bportfolio\b|\bfashion\b|\blifestyle\b",
    "Green energy transition": r"\bsolar\b|\bbatter(y|ies)\b|\benergy storage\b|\brenewable\b|\bgreen\b|\bnet[- ]zero\b|\bsodium\b|\bhydrogen\b|\bcarbon\b",
    "Synergy & integration": r"\bsynerg(y|ies|istic)\b|\bintegrat(e|ed|ion|ing)\b|\bcombin(e|ed|ation)\b|\bwin-win\b",
    "Partnership & capital": r"\bpartner(s|ship|ships)?\b|\binvestors?\b|\bvaluation\b|\bequity value\b|\bcapital\b",
}


def theme_counts(text):
    words = len(re.findall(r"[A-Za-z]+", text))
    counts = {t: len(re.findall(p, text, flags=re.IGNORECASE if t != "Technology & capability" else 0))
              for t, p in THEMES.items()}
    return words, counts


# (1) press releases
deals = pd.read_csv(os.path.join(DATA, "deals", "deals_master.csv"))
pr_map = {  # press-release file prefix -> deal id
    "2012-01-03": "A01", "2014-05-29": "A02", "2017-09-06": "A03", "2017-12-28": "A04", "2018-02-20": "A05",
    "2018-03-23": "A06", "2018-04-13": "A07", "2018-06-29": "A08", "2018-10-17_RIL": "A09",
    "2019-04-03": "A11", "2020-08-18_Reliance_Retail": "A13", "2020-08-29": "A14", "2021-02-28": "A16",
    "2021-07-16": "A17", "2021-08-10": "A18", "2021-10-10_Reliance_New_Energy_Solar_Ltd": "A19",
    "2021-10-10_Reliance_New_Energy_Solar_to": "A19", "2021-12-31": "A20", "2022-02-14_Jio_Platforms": "A22",
    "2022-03-14": "A23", "2022-03-20": "A24", "2022-09-05": "A25", "2022-12-22": "A26", "2023-01-03": "A27",
    "2023-10-04": "A28", "2024-02-28": "A29", "2025-07-18": "A30", "2019-08-12": "B01", "2020-04-22": "B02",
    "2020-07-15": "B03", "2020-09-09": "B04", "2023-08-23": "B05",
}
rows = []
for f in sorted(glob.glob(os.path.join(DATA, "deals", "press_releases", "*.txt"))):
    base = os.path.basename(f)
    did = next((v for k, v in pr_map.items() if base.startswith(k)), None)
    if did is None:
        continue
    text = open(f, errors="ignore").read()
    # drop the boiler-plate "About Reliance/Jio" paragraphs, which repeat in every release
    text = re.split(r"\n\s*About (Reliance|RIL|Jio|Reliance Industries|Reliance Retail)", text)[0]
    w, c = theme_counts(text)
    rows.append({"id": did, "file": base, "words": w, **{k: 1000 * v / w for k, v in c.items()}})
pr = pd.DataFrame(rows).groupby("id").agg({"words": "sum", **{t: "mean" for t in THEMES}}).reset_index()
pr = deals[["id", "group", "deal", "cluster", "motive"]].merge(pr, on="id")
pr.to_csv(os.path.join(RES, "content_press_releases.csv"), index=False)
pr.groupby("cluster")[list(THEMES)].mean().round(2).to_csv(os.path.join(RES, "content_by_cluster.csv"))

# (2) annual reports
if len(sys.argv) > 1:
    ar_rows = []
    for f, fy in [("5003250313.txt", 2013), ("5003250314.txt", 2014), ("RIL-Integrated-AR-2016-17HRF.txt", 2017),
                  ("RIL-AR-2018.txt", 2018), ("ril-annual-report-2019.txt", 2019),
                  ("RIL_Integrated-Annual-Report-2019-2020.txt", 2020), ("RIL-AR-2021.txt", 2021),
                  ("AR_2021-22.txt", 2022), ("RIL-Integrated-Annual-Report-2022-23.txt", 2023),
                  ("RIL-Integrated-Annual-Report-2023-24.txt", 2024), ("RIL-Integrated-Annual-Report-2024-25.txt", 2025),
                  ("RIL-Integrated-Annual-Report-2025-26.txt", 2026)]:
        path = next((os.path.join(d, f) for d in sys.argv[1:] if os.path.exists(os.path.join(d, f))), None)
        if path is None:
            continue
        text = open(path, errors="ignore").read()
        w, c = theme_counts(text)
        acq = len(re.findall(r"\bacqui(re|red|res|ring|sition|sitions)\b", text, flags=re.I))
        ar_rows.append({"fy": fy, "words": w, **{k: 10000 * v / w for k, v in c.items()},
                        "Acquisition mentions": 10000 * acq / w})
    pd.DataFrame(ar_rows).to_csv(os.path.join(RES, "content_annual_reports.csv"), index=False)

pd.set_option("display.width", 250)
print(pd.read_csv(os.path.join(RES, "content_by_cluster.csv")).to_string())
if len(sys.argv) > 1:
    print(pd.read_csv(os.path.join(RES, "content_annual_reports.csv")).round(1).to_string())
