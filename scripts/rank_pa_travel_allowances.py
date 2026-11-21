import glob, os, re

OUT_PATH = "content/04_Dossiers/Public_Accounts/Travel_and_Allowances_Ranking_2025_26.md"

def parse_money(val: str | None) -> float:
    if not val or val == "—":
        return 0.0
    return float(val.replace("$", "").replace(",", "").strip())

def main():
    records = []
    for role, folder in (("Cabinet", "content/02_Cabinet/*.md"), ("Deputy Minister", "content/03_Deputy_Ministers/*.md")):
        for path in sorted(glob.glob(folder)):
            stem = os.path.basename(path)[:-3]
            txt = open(path, encoding="utf-8").read()
            pa_sec = re.search(r"## Public Accounts 2025/26\n(.*?)(?:\n## |\Z)", txt, flags=re.S)
            if not pa_sec:
                continue
            block = pa_sec.group(1)
            comp_m = re.search(r"(?:Base/MLA Comp|Salary & Other Compensation):\s*\*\*(\$[0-9,\.]+)\*\*", block)
            trv_m = re.search(r"Travel:\s*\*\*(\$[0-9,\.]+)\*\*", block)
            allow_m = re.search(r"Allowances/Other:\s*\*\*(\$[0-9,\.]+)\*\*", block)

            comp = parse_money(comp_m.group(1) if comp_m else None)
            trv = parse_money(trv_m.group(1) if trv_m else None)
            allow = parse_money(allow_m.group(1) if allow_m else None)
            total = comp + trv + allow

            folder_slug = folder.split("/")[1]
            link = f"[[{folder_slug}/{stem}|{stem.replace('_', ' ')}]]"
            records.append({
                "stem": stem,
                "link": link,
                "role": role,
                "comp": comp,
                "trv": trv,
                "allow": allow,
                "total": total,
            })

    by_travel = sorted(records, key=lambda r: (-r["trv"], -r["total"]))
    by_total = sorted(records, key=lambda r: (-r["total"], -r["trv"]))

    tot_comp = sum(r["comp"] for r in records)
    tot_trv = sum(r["trv"] for r in records)
    tot_allow = sum(r["allow"] for r in records)

    out = [
        "---",
        'title: "B.C. Public Accounts 2025/26 — Travel, Compensation & Allowances Ranking"',
        "date: 2026-11-20",
        "---",
        "",
        "# B.C. Public Accounts 2025/26 — Travel, Compensation & Allowances Ranking",
        "",
        f"- **Matched Profiles Ranked:** {len(records)}",
        f"- **Aggregate Base/Salary Compensation:** `${tot_comp:,.2f}`",
        f"- **Aggregate Travel:** `${tot_trv:,.2f}`",
        f"- **Aggregate Role/Committee Allowances & Other:** `${tot_allow:,.2f}`",
        f"- **Combined Total:** `${(tot_comp + tot_trv + tot_allow):,.2f}`",
        "",
        "## 1. Ranked by 2025/26 Travel Expenses",
        "",
        "| Rank | Profile | Role | Travel | Base / Salary Comp | Allowances / Other | Combined Total |",
        "| :---: | :--- | :--- | :---: | :---: | :---: | :---: |",
    ]
    for idx, r in enumerate(by_travel, 1):
        out.append(
            f"| {idx} | {r['link']} | {r['role']} | `${r['trv']:,.0f}` | `${r['comp']:,.0f}` | `${r['allow']:,.0f}` | `${r['total']:,.0f}` |"
        )

    out += [
        "",
        "## 2. Ranked by Combined 2025/26 Total (Compensation + Travel + Allowances)",
        "",
        "| Rank | Profile | Role | Combined Total | Base / Salary Comp | Travel | Allowances / Other |",
        "| :---: | :--- | :--- | :---: | :---: | :---: | :---: |",
    ]
    for idx, r in enumerate(by_total, 1):
        out.append(
            f"| {idx} | {r['link']} | {r['role']} | `${r['total']:,.0f}` | `${r['comp']:,.0f}` | `${r['trv']:,.0f}` | `${r['allow']:,.0f}` |"
        )

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(out).strip() + "\n")

    print(f"WROTE {OUT_PATH} ({len(records)} profiles | Total Travel=${tot_trv:,.0f} | Combined=${(tot_comp + tot_trv + tot_allow):,.0f})")

if __name__ == "__main__":
    main()
