import os, glob, re, unicodedata

def norm_key(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "", s.lower())

pds_files = sorted(glob.glob("content/05_Primary_Sources/PDS/*.md"))
pds_by_person = {}
for pf in pds_files:
    base = os.path.basename(pf)[:-3]
    person_part = base.split("__", 1)[0]
    pds_by_person.setdefault(norm_key(person_part), []).append(pf)

zero_files = []
updated_count = 0

for cp in sorted(glob.glob("content/02_Cabinet/*.md")):
    stem = os.path.basename(cp)[:-3]
    recs = pds_by_person.get(norm_key(stem), [])
    raw = open(cp, encoding="utf-8").read()
    body = re.split(r"\n## Primary COI & Gift Disclosures[^\n]*", raw, maxsplit=1)[0].rstrip()

    if not recs:
        zero_files.append(os.path.basename(cp))
        if raw.strip() != body.strip():
            open(cp, "w", encoding="utf-8").write(body + "\n")
        continue

    sec = ["\n\n## Primary COI & Gift Disclosures (2025–2026)"]
    pds26 = None
    for r in sorted(recs):
        fn = os.path.basename(r)[:-3]
        label = fn.split("__", 1)[1] if "__" in fn else fn
        pdf_rel = f"quartz/static/sources/Primary_Records/PDS/{fn}.pdf"
        pdf_link = f" ([PDF](/static/sources/Primary_Records/PDS/{fn}.pdf))" if os.path.exists(pdf_rel) else ""
        sec.append(f"- [[05_Primary_Sources/PDS/{fn}|{label}]]{pdf_link}")
        if fn.endswith("_2026"):
            pds26 = r

    if pds26:
        m = re.search(r"```text\n(.*?)\n```", open(pds26, encoding="utf-8").read(), re.S)
        if m and m.group(1).strip():
            sec.append("\n### 2026 Public Disclosure Statement\n```text\n" + m.group(1).strip() + "\n```")

    open(cp, "w", encoding="utf-8").write(body + "".join(sec) + "\n")
    updated_count += 1

nav = (
    "# B.C. Conservative Government OSINT Vault\n"
    "- [[00_Index/Master_Roster_2026|Master Roster 2026]]\n"
    "- [[04_Dossiers/Cariboo_Chilcotin/Dossier_Cariboo_Gold_Project|Cariboo Gold]]\n"
    "- [[04_Dossiers/Cariboo_Chilcotin/Dossier_Yellowhead_Copper_100Mile|Yellowhead Copper]]\n"
    "- [[04_Dossiers/Cariboo_Chilcotin/Dossier_Tolko_Cariboo_Timber|Tolko Timber]]\n"
    "- [[04_Dossiers/Cariboo_Chilcotin/Dossier_DRIPA_Repeal_Cariboo_Title|DRIPA & Title]]\n"
    "- [[04_Dossiers/Cariboo_Chilcotin/Dossier_Cariboo_Healthcare_CMH_100MileER|CMH & 100 Mile ER]]\n"
    "- [[04_Dossiers/Cariboo_Chilcotin/Dossier_Wildfire_Chilcotin_Recovery|Wildfire & Chilcotin]]\n"
    "- [[04_Dossiers/Cariboo_Chilcotin/Dossier_Highway97_Cariboo_Connector|Highway 97]]\n"
    "- [[04_Dossiers/Lobbying_ORL/External_Appointees_Lobbying_Sweep|ORL Lobbying Sweep]]\n"
)
open("content/_Sidebar.md", "w", encoding="utf-8").write(nav)
open("content/Home.md", "w", encoding="utf-8").write(
    nav
    + "\n## Directories\n"
    + f"- `01_Ministries/` ({len(glob.glob('content/01_Ministries/*'))})\n"
    + f"- `02_Cabinet/` ({len(glob.glob('content/02_Cabinet/*.md'))})\n"
    + f"- `03_Deputy_Ministers/` ({len(glob.glob('content/03_Deputy_Ministers/*'))})\n"
    + f"- `04_Dossiers/` ({len(glob.glob('content/04_Dossiers/*', recursive=True))})\n"
    + f"- `05_Primary_Sources/PDS/` ({len(pds_files)})\n"
)

print(f"UPDATED CABINET FILES: {updated_count}")
print(f"ZERO PDS MATCH ({len(zero_files)}): {zero_files}")
