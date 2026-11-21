import os, re

ROSTER_PATH = "content/00_Index/Master_Roster_2026.md"
AUDIT_PATH = "content/00_Index/Coverage_Gap_Audit_2026.md"

def split_md_row(line: str) -> list[str]:
    # Protect pipes inside [[...]] wikilinks before splitting on table pipes
    protected = re.sub(r"\[\[([^\]]+)\]\]", lambda m: "[[" + m.group(1).replace("|", "§§") + "]]", line.strip())
    parts = [c.strip().replace("§§", "|") for c in protected.strip("|").split("|")]
    return parts

def main():
    lines = open(ROSTER_PATH, encoding="utf-8").read().splitlines()
    data_rows = [ln for ln in lines if ln.startswith("| [[")]

    no_pds = []
    zero_core = []
    no_fr = []

    for ln in data_rows:
        cols = split_md_row(ln)
        if len(cols) < 9:
            continue
        prof, role, pds, orl, sa1a, sa1, pa, pds_pa, fr = cols[:9]
        if pds == "—":
            no_pds.append((prof, role, orl, sa1a, sa1, pa, fr))
        if orl == "—" and sa1a == "—" and sa1 == "—" and pa == "—":
            zero_core.append((prof, role, pds, fr))
        if fr == "—":
            no_fr.append((prof, role, pds, orl, pa))

    out = [
        "---",
        'title: "Coverage Gap Audit 2026 — B.C. Conservative Government Vault"',
        "date: 2026-11-20",
        "---",
        "",
        "# Coverage Gap Audit 2026 — B.C. Conservative Government Vault",
        "",
        f"- **Total Roster Profiles Audited:** {len(data_rows)}",
        f"- **Missing PDS / COI Filings:** {len(no_pds)}",
        f"- **Zero Matches Across ORL, Elections BC (SA1A/SA1), and Public Accounts:** {len(zero_core)}",
        f"- **Zero `FRSearch.aspx` Report Matches:** {len(no_fr)}",
        "",
        "## 1. Profiles Missing PDS / COI Filings",
        "",
        "| Profile | Role | ORL | SA1A | SA1 | PA 25/26 | FRSearch |",
        "| :--- | :--- | :---: | :---: | :---: | :---: | :---: |",
    ]
    for prof, role, orl, sa1a, sa1, pa, fr in no_pds:
        out.append(f"| {prof} | {role} | {orl} | {sa1a} | {sa1} | {pa} | {fr} |")

    out += [
        "",
        "## 2. Profiles with Zero Matches in ORL, SA1A/SA1, and Public Accounts",
        "",
        "| Profile | Role | PDS / COI | FRSearch |",
        "| :--- | :--- | :---: | :---: |",
    ]
    for prof, role, pds, fr in zero_core:
        out.append(f"| {prof} | {role} | {pds} | {fr} |")

    out += [
        "",
        "## 3. Profiles Without `FRSearch.aspx` Filing Rows",
        "",
        "| Profile | Role | PDS / COI | ORL | PA 25/26 |",
        "| :--- | :--- | :---: | :---: | :---: |",
    ]
    for prof, role, pds, orl, pa in no_fr:
        out.append(f"| {prof} | {role} | {pds} | {orl} | {pa} |")

    with open(AUDIT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(out).strip() + "\n")

    print(f"WROTE {AUDIT_PATH} | NO_PDS={len(no_pds)} | ZERO_CORE={len(zero_core)} | NO_FR={len(no_fr)}")

if __name__ == "__main__":
    main()
