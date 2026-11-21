import glob, os, re

sweep_path = "content/04_Dossiers/Elections_BC/Cabinet_DM_Elections_BC_Sweep.md"
txt = open(sweep_path, encoding="utf-8").read()

sections = re.split(r"\n## ", "\n" + txt.strip())
stats = {}

for sec in sections[1:]:
    lines = sec.splitlines()
    page = lines[0].strip()
    for m in re.finditer(r"^### ([A-Za-z0-9_]+) — (\d+) exact rows \(\$([0-9,]+\.\d{2})\)", sec, flags=re.M):
        stem, rows, amt = m.group(1), int(m.group(2)), m.group(3)
        stats.setdefault(stem, {})[page] = (rows, f"${amt}")

linked = 0
for folder in ("content/02_Cabinet/*.md", "content/03_Deputy_Ministers/*.md"):
    for path in sorted(glob.glob(folder)):
        stem = os.path.basename(path)[:-3]
        raw = open(path, encoding="utf-8").read()
        body = re.split(r"\n## Elections BC Contributions[^\n]*", raw, maxsplit=1)[0].rstrip()
        p_stats = stats.get(stem, {})
        if p_stats:
            parts = []
            for pg in ("SA1ASearch.aspx", "SA1Search.aspx"):
                if pg in p_stats:
                    r_cnt, tot = p_stats[pg]
                    parts.append(f"`{pg}`: **{r_cnt}** rows (**{tot}**)")
            block = (
                "\n\n## Elections BC Contributions\n"
                f"- {' | '.join(parts)}\n"
                f"- Full sweep: [[04_Dossiers/Elections_BC/Cabinet_DM_Elections_BC_Sweep|{stem} Elections BC Matches]]\n"
            )
            open(path, "w", encoding="utf-8").write(body + block)
            linked += 1

for nav_file in ("content/_Sidebar.md", "content/Home.md"):
    if os.path.exists(nav_file):
        nav_txt = open(nav_file, encoding="utf-8").read()
        ebc_line = "- [[04_Dossiers/Elections_BC/Cabinet_DM_Elections_BC_Sweep|Elections BC Sweep]]"
        orl_line = "- [[04_Dossiers/Lobbying_ORL/Cabinet_DM_ORL_Sweep|Cabinet & DM ORL Sweep]]"
        if "Cabinet_DM_Elections_BC_Sweep" not in nav_txt:
            if "\n## Directories" in nav_txt:
                nav_txt = nav_txt.replace("\n## Directories", f"{ebc_line}\n{orl_line}\n\n## Directories", 1)
            else:
                nav_txt = nav_txt.rstrip() + f"\n{ebc_line}\n{orl_line}\n"
            open(nav_file, "w", encoding="utf-8").write(nav_txt)

print(f"LINKED ELECTIONS BC INTO {linked} PROFILES & UPDATED NAV")
