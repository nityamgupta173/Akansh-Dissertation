# MBA Dissertation: Mergers & Acquisitions by Reliance Industries Limited

**Title:** Mergers & Acquisitions by Reliance Industries Limited – An Analysis of Strategic Intent and Financial Outcomes
**Student:** Akansh Agarwal (FT-25-205), MBA (Full-Time) 2025–27, FMS, University of Delhi
**Guide:** Dr. Arnav Kumar, Assistant Professor, Finance

## Deliverables
- `dissertation/Akansh_Agarwal_RIL_MA_Dissertation_Draft.docx` – the draft (editable Word file)
- `dissertation/Akansh_Agarwal_RIL_MA_Dissertation_Draft.pdf` – PDF preview of the same file

## Layout
| Folder | Contents |
|---|---|
| `data/prices/` | Daily prices (NSE via Yahoo Finance): RIL, Nifty 50 and seven target companies |
| `data/financials/` | Screener.in statements; `manual/` holds FY2012–14 figures from annual reports and RIL segment data |
| `data/deals/` | RIL press-release index, the text of 52 deal releases, `deals_master.csv` (deal list with strategic coding), `target_events.csv` |
| `analysis/` | Python scripts, numbered in the order they run |
| `results/` | Every table in Chapter 4 as a CSV file |
| `figures/` | Figures used in the dissertation |
| `dissertation/build/` | Node (docx-js) source of the Word document |

## Rebuilding
```bash
python3 analysis/01_prices_to_csv.py && python3 analysis/02_screener_to_csv.py
python3 analysis/10_event_study.py && python3 analysis/15_deal_descriptives.py
python3 analysis/20_financial_ratios.py && python3 analysis/30_prepost_tests.py
python3 analysis/40_content_analysis.py <dir with annual-report .txt files>
python3 analysis/50_figures.py && python3 analysis/60_tables_for_doc.py
cd dissertation/build && ./render.sh     # two-pass build: page numbers for the contents pages
```
