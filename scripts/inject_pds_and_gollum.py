import os, glob, re

for cp in sorted(glob.glob("content/02_Cabinet/*.md")):
    name = os.path.basename(cp)[:-3]
    recs = sorted(glob.glob(f"content/05_Primary_Sources/PDS/{name}__*.md"))
    if not recs: continue
    body = open(cp, encoding="utf-8").read().split("\n## Primary COI & Gift Disclosures")[0].rstrip()
    sec = ["\n\n## Primary COI & Gift Disclosures (2025–2026)"]
    pds26 = None
    for r in recs:
        fn = os.path.basename(r)[:-3]
        sec.append(f"- [[05_Primary_Sources/PDS/{fn}|{fn.split('__',1)[1]}]] ([PDF](/static/sources/Primary_Records/PDS/{fn}.pdf))")
        if fn.endswith("_2026"): pds26 = r
    if pds26:
        m = re.search(r"```text\n(.*?)\n```", open(pds26, encoding="utf-8").read(), re.S)
        if m and m.group(1).strip():
            sec.append("\n### 2026 Public Disclosure Statement\n```text\n" + m.group(1).strip() + "\n```")
    open(cp, "w", encoding="utf-8").write(body + "\n".join(sec) + "\n")

nav = "# B.C. Conservative Government OSINT Vault\n- [[00_Index/Master_Roster_2026|Master Roster 2026]]\n- [[04_Dossiers/Cariboo_Chilcotin/Dossier_Cariboo_Gold_Project|Cariboo Gold]]\n- [[04_Dossiers/Cariboo_Chilcotin/Dossier_Yellowhead_Copper_100Mile|Yellowhead Copper]]\n- [[04_Dossiers/Cariboo_Chilcotin/Dossier_Tolko_Cariboo_Timber|Tolko Timber]]\n- [[04_Dossiers/Cariboo_Chilcotin/Dossier_DRIPA_Repeal_Cariboo_Title|DRIPA & Title]]\n- [[04_Dossiers/Cariboo_Chilcotin/Dossier_Cariboo_Healthcare_CMH_100MileER|CMH & 100 Mile ER]]\n- [[04_Dossiers/Cariboo_Chilcotin/Dossier_Wildfire_Chilcotin_Recovery|Wildfire & Chilcotin]]\n- [[04_Dossiers/Cariboo_Chilcotin/Dossier_Highway97_Cariboo_Connector|Highway 97]]\n- [[04_Dossiers/Lobbying_ORL/External_Appointees_Lobbying_Sweep|ORL Lobbying Sweep]]\n"
open("content/_Sidebar.md", "w").write(nav)
open("content/Home.md", "w").write(nav + "\n## Directories\n- `01_Ministries/` (19)\n- `02_Cabinet/` (25)\n- `03_Deputy_Ministers/` (24)\n- `04_Dossiers/` (8)\n- `05_Primary_Sources/PDS/` (68)\n")
print("DONE: INJECTED PDS & CREATED GOLLUM NAV")
