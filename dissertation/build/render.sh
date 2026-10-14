#!/bin/bash
# Two-pass build: render, map pages, rebuild with page numbers, render again.
set -e
B=/home/user/Akansh-Dissertation/dissertation/build
R=/tmp/claude-0/-home-user-Akansh-Dissertation/d49a1ee6-f965-5a06-8754-87712bb297ae/scratchpad/render
SOFF=/root/.claude/skills/synced/d7b78281-39c8-43f1-a5ac-521fda742908_1bf9b61e-0b98-44e8-9b7c-b11d955df36c/docx/scripts/office/soffice.py
DOCX=/home/user/Akansh-Dissertation/dissertation/Akansh_Agarwal_RIL_MA_Dissertation_Draft.docx
mkdir -p $R
render() { cp $DOCX $R/draft.docx; (cd $R && python3 $SOFF --headless --convert-to pdf draft.docx >/dev/null 2>&1); }
node $B/build.js >/dev/null
render
python3 $B/pagemap.py $R/draft.pdf $B/registry.json $B/pagemap.json
node $B/build.js $B/pagemap.json >/dev/null
render
python3 $B/pagemap.py $R/draft.pdf $B/registry.json $B/pagemap2.json
cmp -s <(python3 -c "import json;print(json.dumps(json.load(open('$B/pagemap.json')),sort_keys=True))") <(python3 -c "import json;print(json.dumps(json.load(open('$B/pagemap2.json')),sort_keys=True))") && echo "page numbers stable" || echo "PAGE NUMBERS CHANGED"
pdfinfo $R/draft.pdf | grep Pages
