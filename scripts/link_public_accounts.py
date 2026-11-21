import glob, os, re

sweep_path = "content/04_Dossiers/Public_Accounts/Cabinet_DM_Public_Accounts_Sweep.md"
txt = open(sweep_path, encoding="utf-8").read()

counts = {}
for m in re.finditer(r"^### ([A-Za-z0-9_]+) \((Cabinet|Deputy Minister)\) — (\d+) matches", txt, flags=re.M):
    stem, _role, cnt = m.group(1), m.group(2), int(m.group(3))
    counts[stem] = cnt

linked = 0
for folder in ("content/02_Cabinet/*.md", "content/03_Deputy_Ministers/*.md"):
    for path in sorted(glob.glob(folder)):
        stem = os.path.basename(path)[:-3]
        raw = open(path, encoding="utf-8").read()
        body = re.split(r"\n## Public Accounts 2025/26[^\n]*", raw, maxsplit=1)[0].rstrip()
        if stem in counts:
            cnt = counts[stem]
            block = (
                "\n\n## Public Accounts 2025/26\n"
                f"- CRF Detailed Schedules matches: **{cnt}**\n"
                f"- Full sweep: [[04_Dossiers/Public_Accounts/Cabinet_DM_Public_Accounts_Sweep|{stem} Public Accounts Matches]]\n"
            )
            open(path, "w", encoding="utf-8").write(body + block)
            linked += 1

for nav_file in ("content/_Sidebar.md", "content/Home.md"):
    if os.path.exists(nav_file):
        nav_txt = open(nav_file, encoding="utf-8").read()
        pa_line = "- [[04_Dossiers/Public_Accounts/Cabinet_DM_Public_Accounts_Sweep|Public Accounts 2025/26 Sweep]]"
        if "Cabinet_DM_Public_Accounts_Sweep" not in nav_txt:
            if "\n## Directories" in nav_txt:
                nav_txt = nav_txt.replace("\n## Directories", f"{pa_line}\n\n## Directories", 1)
            else:
                nav_txt = nav_txt.rstrip() + f"\n{pa_line}\n"
            open(nav_file, "w", encoding="utf-8").write(nav_txt)

print(f"LINKED PUBLIC ACCOUNTS INTO {linked} PROFILES")
