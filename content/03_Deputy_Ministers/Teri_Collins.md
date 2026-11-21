---
date: 2026-11-20
title: "Teri Collins"
type: person
role: "Deputy Minister of Social Development"
ministry: "[[01_Ministries/17_Social_Development]]"
cabinet_minister: "Claire Rattée (Deputy Premier)"
appointment_type: "Lateral Reassignment (Career Deputy)"
lobbyist_ties: "Pending BC ORL Housing & Social Development filings check"
compensation_sofi: "Pending FY2025-26 BC Public Accounts CRF pull"
status: verified
tags:
  - person
  - deputy-minister
  - social-development
  - bc-housing
  - lateral-move
---

# Teri Collins

## Current Role
- **Title:** Deputy Minister of Social Development
- **Ministry:** [[01_Ministries/17_Social_Development]]
- **Cabinet Minister:** Claire Rattée (Deputy Premier)

## Career & Background Summary
- **Ministry of Housing and Municipal Affairs (Dec 2022–Oct 2026):** Appointed Deputy Minister of the newly created Ministry of Housing on December 7, 2022; served as

sed -i 's/| Pending |/| Complete |/g' ~/Conservative_Government/00_Index/Master_Roster_2026.md

mkdir -p ~/Conservative_Government/03_Sources/{Public_Accounts,Lobbying_ORL,External_Appointees}

# 1. FY 2025/26 BC Public Accounts — Consolidated Revenue Fund Detailed Schedules of Payments (8.7 MB)
curl -L -o ~/Conservative_Government/03_Sources/Public_Accounts/pa-2025-26-crf-detailed-schedules-of-payments.pdf \
  "https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2025-26/pa-2025-26-crf-detailed-schedules-of-payments.pdf"

# 2. Kim Henderson — 2016/17 BC Budget & Fiscal Plan (signed as DM Finance) & Alberta MacKinnon Panel page
curl -L -o ~/Conservative_Government/03_Sources/External_Appointees/Henderson_BC_Budget_2016.pdf \
  "https://bcbudget.gov.bc.ca/2016/bfp/2016_budget_and_fiscal_plan.pdf"
curl -L -o ~/Conservative_Government/03_Sources/External_Appointees/Henderson_Alberta_MacKinnon_Panel.html \
  "https://www.alberta.ca/mackinnon-report-on-finances"

# 3. Geoff Cowper, KC — Fasken "The Transition Trap" (Oct 27, 2026) & Partner Bio
curl -L -o ~/Conservative_Government/03_Sources/External_Appointees/Cowper_Fasken_Transition_Trap_2026-10-27.html \
  "https://www.fasken.com/en/knowledge/2026/10/the-transition-trap"
curl -L -o ~/Conservative_Government/03_Sources/External_Appointees/Cowper_Fasken_Profile.html \
  "https://www.fasken.com/en/geoffrey-cowper"

# 4. Steve Vanagas — TransLink Board Meeting Packages (Apr 2025 & Oct 1, 2025) & 2023 SOFI Report
curl -L -o ~/Conservative_Government/03_Sources/External_Appointees/Vanagas_TransLink_Board_2025-10-01.pdf \
  "https://www.translink.ca/-/media/translink/documents/about-translink/governance-and-board/board-of-directors/board-minutes-and-reports/2025/october/public-board-meeting-oct-1.pdf"
curl -L -o ~/Conservative_Government/03_Sources/External_Appointees/Vanagas_TransLink_SOFI_2023_theBreaker.html \
  "https://thebreaker.news/business/translink-pay-parade/"

# 5. Janis Simpkins — BC Lobbyists Registry (ORL) Tolko Registration #10607-3295 & Activity Reports
curl -L -o ~/Conservative_Government/03_Sources/Lobbying_ORL/Simpkins_Tolko_Client_Summary_3295.html \
  "https://www.lobbyistsregistrar.bc.ca/app/secure/orl/lrs/do/clntSmmry?clientOrgCorpNumber=3295&wbdisable=true"
curl -L -o ~/Conservative_Government/03_Sources/Lobbying_ORL/Simpkins_ORL_3295-35972_2024-06.html \
  "https://lobbyistsregistrar.bc.ca/app/secure/orl/lrs/do/cmmLgPblcVw?comlogId=35972"
curl -L -o ~/Conservative_Government/03_Sources/Lobbying_ORL/Simpkins_ORL_3295-39664_2025-02.html \
  "https://lobbyistsregistrar.bc.ca/app/secure/orl/lrs/do/cmmLgPblcVw?comlogId=39664"
curl -L -o ~/Conservative_Government/03_Sources/Lobbying_ORL/Simpkins_ORL_Forests_2025-05.html \
  "https://www.lobbyistsregistrar.bc.ca/app/secure/orl/lrs/do/rcntGiCmLgs?cid=40095&dt=2025-05"

python3 - << 'PYEOF'
import os, re, subprocess, glob

pdf_path = os.path.expanduser("~/Conservative_Government/03_Sources/Public_Accounts/pa-2025-26-crf-detailed-schedules-of-payments.pdf")
out_md   = os.path.expanduser("~/Conservative_Government/03_Sources/Public_Accounts/FY2025-26_Deputy_Minister_Compensation.md")
people_dir = os.path.expanduser("~/Conservative_Government/02_People")

# Extract pages 10 to 16 (covers DM/ADM schedule + buffer) using pdftotext
try:
    text = subprocess.check_output(["pdftotext", "-layout", "-f", "10", "-l", "16", pdf_path, "-"], text=True)
except FileNotFoundError:
    raise SystemExit("Please install poppler-utils (pdftotext) first: sudo apt install poppler-utils  OR  brew install poppler")

targets = {
    "Tom_McCarthy.md":     ("MCCARTHY", "TOM"),
    "Michelle_Koski.md":   ("KOSKI", "MICHELLE"),
    "Kaye_Krishna.md":     ("KRISHNA", "KATHRYN"),
    "Silas_Brownsey.md":   ("BROWNSEY", "SILAS"),
    "Fazil_Mihlar.md":     ("MIHLAR", "FAZIL"),
    "Bobbi_Plecas.md":     ("PLECAS", "BOBBI"),
    "Nate_Amann-Blake.md": ("AMANN-BLAKE", "NATHANIEL"),
    "Lori_Halls.md":       ("HALLS", "LORI"),
    "Heather_Wood.md":     ("WOOD", "HEATHER"),
    "Debbie_Godfrey.md":   ("GODFREY", "DEBBIE"),
    "John_Davison.md":     ("DAVISON", "JOHN"),
    "Peter_Pokorny.md":    ("POKORNY", "PETER"),
    "Alex_MacLennan.md":   ("MACLENNAN", "ALEX"),
    "Jonathan_Dube.md":    ("DUBE", "JONATHAN"),
    "Trevor_Hughes.md":    ("HUGHES", "TREVOR"),
    "Tara_Richards.md":    ("RICHARDS", "TARA"),
    "Lorie_Hrycuik.md":    ("HRYCUIK", "LORIE"),
    "Teri_Collins.md":     ("COLLINS", "TERI"),
    "Keith_Godin.md":      ("GODIN", "KEITH"),
    "Kevin_Jardine.md":    ("JARDINE", "KEVIN"),
}

rows = []
    # Match LAST, FIRST ... SALARY  TRAVEL on same line (handling optional hyphen/accent/middle initial)
    pattern = re.compile(rf"^\s*{re.escape(last).replace('-', '[-–]')},\s*{re.escape(first)}[^\d\n]*?([\d,]+)\s+([\d,]+)\s*$", re.MULTILINE | re.IGNORECASE)
    m = pattern.search(text)
    if not m:
        # Fallback: match last name + first 3 letters of first name
        pattern2 = re.compile(rf"^\s*{re.escape(last).replace('-', '[-–]')},\s*{re.escape(first[:3])}[^\d\n]*?([\d,]+)\s+([\d,]+)\s*$", re.MULTILINE | re.IGNORECASE)
        m = pattern2.search(text)
    if m:
        sal, trv = m.group(1), m.group(2)
        val = f'"FY2025-26 BC Public Accounts CRF: Salary ${sal} | Travel ${trv}"'
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            if "compensation_sofi:" in content:
                content = re.sub(r'^compensation_sofi:.*$', f'compensation_sofi: {val}', content, flags=re.MULTILINE)
            else:
                content = content.replace("status:", f"compensation_sofi: {val}\nstatus:", 1)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
    else:

with open(out_md, "w", encoding="utf-8") as f:
    f.write("---\ntitle: \"FY 2025/26 BC Public Accounts — Deputy Minister Compensation Extract\"\ntype: source\nsource_pdf: \"pa-2025-26-crf-detailed-schedules-of-payments.pdf\"\n---\n\n")
    f.write("# FY 2025/26 BC Public Accounts — Deputy Minister Compensation\n\n")
    f.write("Source: [BC Public Accounts 2025/26 CRF Detailed Schedules of Payments (PDF)](https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/government-finances/public-accounts/2025-26/pa-2025-26-crf-detailed-schedules-of-payments.pdf)\n\n")
    f.write("| Appointee | FY2025/26 Salary | FY2025/26 Travel |\n|---|---|---|\n")
    f.write("\n".join(rows) + "\n")

print("Extraction complete! Summary written to:", out_md)
print("\n".join(rows))
PYEOF
