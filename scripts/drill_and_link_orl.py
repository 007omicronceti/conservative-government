import glob, os, re

sweep_path = "content/04_Dossiers/Lobbying_ORL/Cabinet_DM_ORL_Sweep.md"
txt = open(sweep_path, encoding="utf-8").read()

zero_six = [
    "Caroline_Elliott",
    "Carson_Binda",
    "Cathie_Ounsted",
    "Jessy_Sahota",
    "Ryan_Peterson",
    "Zeeshan_Wahla",
]

print("=== DRILL: 6 ZERO-PDS PROFILES IN ORL SWEEP ===")
for name in zero_six:
    matches = re.findall(rf"(### {re.escape(name)} \(\d+ row matches\)\n(?:- .*\n)*)", txt)
    if not matches:
        print(f"\n[{name}] -> NO HITS")
    else:
        for m in matches:
            print(f"\n{m.strip()}")

# Parse counts per section (REGISTRATIONS vs LARS) for linking
sections = txt.split("\n## ")
section_counts = {}
for sec in sections[1:]:
    sec_title = sec.splitlines()[0].strip()
    for m in re.finditer(r"### ([A-Za-z0-9_]+) \((\d+) row matches\)", sec):
        stem, cnt = m.group(1), int(m.group(2))
        section_counts.setdefault(stem, {})[sec_title] = cnt

linked = 0
for folder in ("content/02_Cabinet/*.md", "content/03_Deputy_Ministers/*.md"):
    for path in sorted(glob.glob(folder)):
        stem = os.path.basename(path)[:-3]
        raw = open(path, encoding="utf-8").read()
        body = re.split(r"\n## ORL Lobbying Registry[^\n]*", raw, maxsplit=1)[0].rstrip()
        cnts = section_counts.get(stem, {})
        reg_c = cnts.get("REGISTRATIONS", 0)
        lar_c = cnts.get("LARS", 0)

        if reg_c or lar_c:
            block = (
                "\n\n## ORL Lobbying Registry\n"
                f"- Registry/Gifts row matches: **{reg_c}** | Lobbying Activity Reports (LAR) row matches: **{lar_c}**\n"
                f"- Full sweep: [[04_Dossiers/Lobbying_ORL/Cabinet_DM_ORL_Sweep|{stem} ORL Matches]]\n"
            )
            open(path, "w", encoding="utf-8").write(body + block)
            linked += 1

print(f"\n=== LINKED ORL SUMMARY INTO {linked} PROFILES ===")
