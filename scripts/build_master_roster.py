import glob, os, re

os.makedirs("content/00_Index", exist_ok=True)
out_path = "content/00_Index/Master_Roster_2026.md"

rows = []
tot_pds_profiles = 0
tot_orl_profiles = 0
tot_ebc_profiles = 0
tot_pa_profiles = 0
tot_pds_pa_links = 0
tot_fr_profiles = 0

for role_label, folder in (("Cabinet", "content/02_Cabinet/*.md"), ("Deputy Minister", "content/03_Deputy_Ministers/*.md")):
    for path in sorted(glob.glob(folder)):
        stem = os.path.basename(path)[:-3]
        rel_link = f"[[{folder.split('/')[1]}/{stem}|{stem.replace('_', ' ')}]]"
        txt = open(path, encoding="utf-8").read()

        pds_links = re.findall(r"\[\[05_Primary_Sources/PDS/([^\|\]]+)", txt)
        if pds_links:
            tot_pds_profiles += 1
            has_2026 = any(x.endswith("_2026") for x in pds_links)
            pds_cell = f"{len(pds_links)} files" + (" (2026)" if has_2026 else "")
        else:
            pds_cell = "—"

        orl_m = re.search(
            r"Registry/Gifts row matches:\s*\*\*(\d+)\*\*\s*\|\s*Lobbying Activity Reports \(LAR\) row matches:\s*\*\*(\d+)\*\*",
            txt,
        )
        if orl_m:
            reg_c, lar_c = int(orl_m.group(1)), int(orl_m.group(2))
            tot_orl_profiles += 1
            orl_cell = f"{reg_c} reg / {lar_c} LAR"
        else:
            orl_cell = "—"

        ebc_sec = re.search(r"## Elections BC Contributions\n- ([^\n]+)", txt)
        if ebc_sec:
            tot_ebc_profiles += 1
            line = ebc_sec.group(1)
            sa1a_m = re.search(r"`SA1ASearch\.aspx`:\s*\*\*(\d+)\*\* rows \(\*\*(\$[0-9,\.]+)\*\*\)", line)
            sa1_m = re.search(r"`SA1Search\.aspx`:\s*\*\*(\d+)\*\* rows \(\*\*(\$[0-9,\.]+)\*\*\)", line)
            sa1a_cell = f"{sa1a_m.group(1)} ({sa1a_m.group(2)})" if sa1a_m else "—"
            sa1_cell = f"{sa1_m.group(1)} ({sa1_m.group(2)})" if sa1_m else "—"
        else:
            sa1a_cell = "—"
            sa1_cell = "—"

        pa_sec = re.search(r"## Public Accounts 2025/26\n(.*?)(?:\n## |\Z)", txt, flags=re.S)
        if pa_sec:
            tot_pa_profiles += 1
            pa_block = pa_sec.group(1)
            comp_m = re.search(r"(?:Base/MLA Comp|Salary & Other Compensation):\s*\*\*(\$[0-9,\.]+)\*\*", pa_block)
            trv_m = re.search(r"Travel:\s*\*\*(\$[0-9,\.]+)\*\*", pa_block)
            comp_val = comp_m.group(1) if comp_m else "—"
            trv_val = trv_m.group(1) if trv_m else "—"
            pa_cell = f"{comp_val} comp / {trv_val} trv"
        else:
            pa_cell = "—"

        pds_pa_sec = re.search(r"## PDS Entity Cross-Check[^\n]*\n(.*?)(?:\n## |\Z)", txt, flags=re.S)
        if pds_pa_sec:
            tot_pds_pa_links += 1
            ent_hits = len(re.findall(r"^- \*\*[^*]+\*\*", pds_pa_sec.group(1), flags=re.M))
            pds_pa_cell = f"{ent_hits} hit(s)" if ent_hits else "Linked"
        else:
            pds_pa_cell = "—"

        fr_sec = re.search(r"## Elections BC Financial Reports \(FRSearch\)\n(.*?)(?:\n## |\Z)", txt, flags=re.S)
        if fr_sec:
            tot_fr_profiles += 1
            fr_m = re.search(r"Matched `FRSearch\.aspx` rows:\s*\*\*(\d+)\*\*", fr_sec.group(1))
            fr_cell = f"{fr_m.group(1)} row(s)" if fr_m else "Matched"
        else:
            fr_cell = "—"

        rows.append(
            f"| {rel_link} | {role_label} | {pds_cell} | {orl_cell} | {sa1a_cell} | {sa1_cell} | {pa_cell} | {pds_pa_cell} | {fr_cell} |"
        )

header = [
    "# Master Roster 2026 — B.C. Conservative Government OSINT Index",
    "",
    f"- **Total Profiles:** {len(rows)}",
    f"- **With PDS/COI Filings:** {tot_pds_profiles} / {len(rows)}",
    f"- **With ORL Lobbying Matches:** {tot_orl_profiles} / {len(rows)}",
    f"- **With Elections BC Contribution Matches:** {tot_ebc_profiles} / {len(rows)}",
    f"- **With Public Accounts 2025/26 Matches:** {tot_pa_profiles} / {len(rows)}",
    f"- **With PDS -> PA Entity Matches:** {tot_pds_pa_links} / {len(rows)}",
    f"- **With Elections BC `FRSearch` Matches:** {tot_fr_profiles} / {len(rows)}",
    "",
    "## Cross-Reference Matrix",
    "",
    "| Profile | Role | PDS / COI Filings | ORL (Reg / LAR) | Elections BC `SA1A` | Elections BC `SA1` | Public Accounts 25/26 | PDS -> PA | EBC `FRSearch` |",
    "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
]

with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(header + rows) + "\n")

print(
    f"WROTE {out_path} ({len(rows)} rows | PDS={tot_pds_profiles} | ORL={tot_orl_profiles} | "
    f"EBC={tot_ebc_profiles} | PA={tot_pa_profiles} | PDS_PA={tot_pds_pa_links} | FR={tot_fr_profiles})"
)
