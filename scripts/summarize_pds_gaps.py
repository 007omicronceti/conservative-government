import re

ROSTER_PATH = "content/00_Index/Master_Roster_2026.md"
OUT_PATH = "content/00_Index/PDS_Gap_Breakdown_2026.md"

def split_md_row(line: str) -> list[str]:
    protected = re.sub(r"\[\[([^\]]+)\]\]", lambda m: "[[" + m.group(1).replace("|", "§§") + "]]", line.strip())
    return [c.strip().replace("§§", "|") for c in protected.strip("|").split("|")]

def main():
    lines = open(ROSTER_PATH, encoding="utf-8").read().splitlines()
    data_rows = [ln for ln in lines if ln.startswith("| [[")]

    missing_by_role = {"Cabinet": [], "Deputy Minister": []}
    for ln in data_rows:
        cols = split_md_row(ln)
        if len(cols) < 9:
            continue
        prof, role, pds, orl, sa1a, sa1, pa, pds_pa, fr = cols[:9]
        if pds == "—":
            has_core = any(x != "—" for x in (orl, sa1a, sa1, pa, fr))
            missing_by_role.setdefault(role, []).append((prof, orl, sa1a, sa1, pa, fr, has_core))

    cab = missing_by_role.get("Cabinet", [])
    dm = missing_by_role.get("Deputy Minister", [])
    cab_active = sum(1 for r in cab if r[6])
    dm_active = sum(1 for r in dm if r[6])

    out = [
        "---",
        'title: "PDS / COI Filing Gap Breakdown 2026 — B.C. Conservative Government"',
        "date: 2026-11-20",
        "---",
        "",
        "# PDS / COI Filing Gap Breakdown 2026",
        "",
        f"- **Total Profiles Missing PDS/COI Disclosures:** {len(cab) + len(dm)} / {len(data_rows)}",
        f"- **Cabinet Ministers Missing PDS/COI:** {len(cab)} ({cab_active} have ORL/EBC/PA/FR matches; {len(cab) - cab_active} have zero external matches)",
        f"- **Deputy Ministers Missing PDS/COI:** {len(dm)} ({dm_active} have ORL/EBC/PA/FR matches; {len(dm) - dm_active} have zero external matches)",
        "",
        "## 1. Cabinet Ministers Missing PDS / COI Filings",
        "",
        "| Profile | ORL (Reg / LAR) | EBC `SA1A` | EBC `SA1` | Public Accounts 25/26 | EBC `FRSearch` |",
        "| :--- | :---: | :---: | :---: | :---: | :---: |",
    ]
    for prof, orl, sa1a, sa1, pa, fr, _ in cab:
        out.append(f"| {prof} | {orl} | {sa1a} | {sa1} | {pa} | {fr} |")

    out += [
        "",
        "## 2. Deputy Ministers Missing PDS / COI Filings",
        "",
        "| Profile | ORL (Reg / LAR) | EBC `SA1A` | EBC `SA1` | Public Accounts 25/26 | EBC `FRSearch` |",
        "| :--- | :---: | :---: | :---: | :---: | :---: |",
    ]
    for prof, orl, sa1a, sa1, pa, fr, _ in dm:
        out.append(f"| {prof} | {orl} | {sa1a} | {sa1} | {pa} | {fr} |")

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(out).strip() + "\n")

    print(f"WROTE {OUT_PATH} (Cabinet missing PDS={len(cab)} | DM missing PDS={len(dm)})")

if __name__ == "__main__":
    main()
