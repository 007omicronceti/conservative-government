import glob, os, re, unicodedata

LAYOUT_TXT = "data_cache/pa_2025_26_layout.txt"
OUT_PATH = "content/04_Dossiers/Public_Accounts/Cabinet_DM_Public_Accounts_Layout.md"

NUM_RE = re.compile(r"\b\d{1,3}(?:,\d{3})+\b|\b\d{3,}\b")

def norm_words(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s.lower())).strip()

def load_profiles():
    profiles = []
    for role, folder in (("Cabinet", "content/02_Cabinet/*.md"), ("Deputy Minister", "content/03_Deputy_Ministers/*.md")):
        for path in sorted(glob.glob(folder)):
            stem = os.path.basename(path)[:-3]
            parts = [p for p in stem.split("_") if p and len(p) > 1]
            if len(parts) >= 2:
                full = norm_words(" ".join(parts))
                first = norm_words(parts[0])
                last = norm_words(parts[-1])
                profiles.append({
                    "stem": stem,
                    "path": path,
                    "role": role,
                    "full": full,
                    "first": first,
                    "last": last,
                })
    return profiles

def line_matches_profile(line: str, p: dict) -> bool:
    nln = norm_words(line)
    if not nln:
        return False
    if p["full"] and p["full"] in nln:
        return True
    for m in re.finditer(rf"\b{re.escape(p['last'])}\b\s*,?\s*([a-z0-9]+)", nln):
        given = m.group(1)
        if given == p["first"] or (len(given) == 1 and given == p["first"][0]):
            return True
    return False

def is_new_person_line(line: str) -> bool:
    s = line.strip()
    return bool(re.match(r"^[A-ZÀ-ÿ][A-ZÀ-ÿ'\-\s]+,\s*[A-ZÀ-ÿ]", s))

def parse_mla_block(lines: list[str], idx: int) -> dict:
    block = [lines[idx]]
    for j in range(idx + 1, min(len(lines), idx + 9)):
        if is_new_person_line(lines[j]):
            break
        block.append(lines[j])

    raw_name = block[0].strip()
    constituency = ""
    base_nums = []
    allowances = []
    pending_alw = []
    alw_nums = []

    for sub in block[1:]:
        clean_sub = re.sub(r"\s*\.{3,}\s*", "  ", sub).strip()
        if not clean_sub:
            continue
        nums = NUM_RE.findall(clean_sub)
        text_only = NUM_RE.sub("", clean_sub).strip(" .-")

        if text_only.lower().startswith("allowance"):
            if pending_alw:
                t = " ".join(pending_alw)
                allowances.append(f"{t}: ${alw_nums[0]}" if alw_nums else t)
            pending_alw = [text_only]
            alw_nums = list(nums)
        elif pending_alw and text_only.lower() in ("special committee", "committee", "whole"):
            pending_alw.append(text_only)
            if nums:
                alw_nums.extend(nums)
        elif pending_alw and nums and not alw_nums:
            alw_nums.extend(nums)
        elif nums and not base_nums:
            base_nums = nums
        elif text_only and not constituency and text_only.lower() not in ("special committee", "committee", "whole"):
            constituency = text_only

    if pending_alw:
        t = " ".join(pending_alw)
        allowances.append(f"{t}: ${alw_nums[0]}" if alw_nums else t)

    first_clean = re.sub(r"\s*\.{3,}\s*", "  ", block[0]).strip()
    first_nums = NUM_RE.findall(first_clean)
    if first_nums:
        raw_name = NUM_RE.sub("", first_clean).strip()
        base_nums = first_nums

    return {
        "schedule": "Members' Compensation",
        "raw_name": raw_name,
        "constituency": constituency,
        "numbers": base_nums,
        "allowances": allowances,
    }

def _unused_parse_mla_block(lines: list[str], idx: int) -> dict:
    block = [lines[idx]]
    for j in range(idx + 1, min(len(lines), idx + 9)):
        if is_new_person_line(lines[j]):
            break
        block.append(lines[j])

    raw_name = block[0].strip()
    constituency = ""
    base_nums = []
    allowances = []

    i = 1
    while i < len(block):
        clean_sub = re.sub(r"\s*\.{3,}\s*", "  ", block[i]).strip()
        if not clean_sub:
            i += 1
            continue
        nums = NUM_RE.findall(clean_sub)
        text_only = NUM_RE.sub("", clean_sub).strip(" .-")

        if text_only.lower().startswith("allowance"):
            title_parts = [text_only]
            alw_nums = list(nums)
            k = i + 1
            while k < len(block):
                nxt_clean = re.sub(r"\s*\.{3,}\s*", "  ", block[k]).strip()
                if not nxt_clean:
                    k += 1
                    continue
                nxt_nums = NUM_RE.findall(nxt_clean)
                nxt_text = NUM_RE.sub("", nxt_clean).strip(" .-")
                if nxt_text.lower().startswith("allowance"):
                    break
                if nxt_text and not alw_nums:
                    title_parts.append(nxt_text)
                    if nxt_nums:
                        alw_nums.extend(nxt_nums)
                        k += 1
                        break
                elif nxt_nums and not alw_nums:
                    alw_nums.extend(nxt_nums)
                    k += 1
                    break
                else:
                    break
            full_title = " ".join(title_parts)
            allowances.append(f"{full_title}: ${alw_nums[0]}" if alw_nums else full_title)
            i = k
            continue

        if nums and not base_nums:
            base_nums = nums
        elif text_only and not constituency:
            constituency = text_only
        i += 1

    first_clean = re.sub(r"\s*\.{3,}\s*", "  ", block[0]).strip()
    first_nums = NUM_RE.findall(first_clean)
    if first_nums:
        raw_name = NUM_RE.sub("", first_clean).strip()
        base_nums = first_nums

    return {
        "schedule": "Members' Compensation",
        "raw_name": raw_name,
        "constituency": constituency,
        "numbers": base_nums,
        "allowances": allowances,
    }

def parse_dm_block(lines: list[str], idx: int) -> dict:
    block = [lines[idx]]
    for j in range(idx + 1, min(len(lines), idx + 4)):
        if is_new_person_line(lines[j]):
            break
        block.append(lines[j])

    raw_name = re.sub(r"\s*\.{3,}\s*", "  ", block[0]).strip()
    nums = NUM_RE.findall(raw_name)
    raw_name = NUM_RE.sub("", raw_name).strip()

    if not nums:
        for sub in block[1:]:
            clean_sub = re.sub(r"\s*\.{3,}\s*", "  ", sub).strip()
            found = NUM_RE.findall(clean_sub)
            if found:
                nums.extend(found)
                break

    return {
        "schedule": "Deputy Ministers Salary & Travel",
        "raw_name": raw_name,
        "numbers": nums,
    }

def main():
    if not os.path.exists(LAYOUT_TXT):
        raise SystemExit(f"Missing {LAYOUT_TXT}")

    profiles = load_profiles()
    pages = open(LAYOUT_TXT, encoding="utf-8", errors="replace").read().split("\x0c")

    results = {}
    for pno, page_txt in enumerate(pages, start=1):
        lines = [ln.rstrip() for ln in page_txt.splitlines() if ln.strip()]
        head_blob = " ".join(lines[:6]).upper()
        is_mla_page = "MEMBERS' COMPENSATION" in head_blob or "MEMBERS OF THE LEGISLATIVE ASSEMBLY" in head_blob
        is_dm_page = "DEPUTY MINISTERS" in head_blob

        for idx, ln in enumerate(lines):
            for p in profiles:
                if line_matches_profile(ln, p):
                    if is_mla_page:
                        rec = parse_mla_block(lines, idx)
                    elif is_dm_page:
                        rec = parse_dm_block(lines, idx)
                    else:
                        clean_ln = re.sub(r"\s*\.{3,}\s*", " | ", ln.strip())
                        rec = {
                            "schedule": "Other CRF Schedule",
                            "raw_name": clean_ln,
                            "numbers": NUM_RE.findall(clean_ln),
                        }
                    rec["page"] = pno
                    results.setdefault(p["stem"], []).append(rec)

    out_lines = [
        "# B.C. Public Accounts 2025/26 — Parsed Compensation & Travel Schedules",
        "",
        f"- **Source:** `pa-2025-26-crf-detailed-schedules-of-payments.pdf`",
        f"- **Matched Profiles:** {len(results)} / {len(profiles)}",
        "",
    ]

    updated_profiles = 0
    for p in profiles:
        recs = results.get(p["stem"])
        if not recs:
            continue

        out_lines.append(f"### {p['stem']} ({p['role']})")
        profile_bullets = []

        for r in recs:
            nums = r.get("numbers", [])
            if r["schedule"] == "Members' Compensation":
                comp = f"${nums[0]}" if len(nums) >= 1 else "—"
                living = f"${nums[1]}" if len(nums) >= 2 else "—"
                travel = f"${nums[2]}" if len(nums) >= 3 else "—"
                constit = f" ({r['constituency']})" if r.get("constituency") else ""
                line = (
                    f"- **p.{r['page']} — Members' Compensation{constit}:** "
                    f"Base/MLA Comp: **{comp}** | Capital City Living Allowance: **{living}** | Travel: **{travel}**"
                )
                out_lines.append(line)
                profile_bullets.append(line)
                for alw in r.get("allowances", []):
                    alw_line = f"- **Role Allowance:** {alw}"
                    out_lines.append(alw_line)
                    profile_bullets.append(alw_line)
            elif r["schedule"] == "Deputy Ministers Salary & Travel":
                sal = f"${nums[0]}" if len(nums) >= 1 else "—"
                trv = f"${nums[1]}" if len(nums) >= 2 else "—"
                line = (
                    f"- **p.{r['page']} — Deputy Ministers Salary & Travel:** "
                    f"Salary & Other Compensation: **{sal}** | Travel: **{trv}**"
                )
                out_lines.append(line)
                profile_bullets.append(line)
            else:
                line = f"- **p.{r['page']} — {r['schedule']}:** `{r['raw_name']}`"
                out_lines.append(line)
                profile_bullets.append(line)

        out_lines.append("")

        raw_md = open(p["path"], encoding="utf-8").read()
        body = re.split(r"\n## Public Accounts 2025/26[^\n]*", raw_md, maxsplit=1)[0].rstrip()
        new_sec = (
            "\n\n## Public Accounts 2025/26\n"
            + "\n".join(profile_bullets)
            + f"\n- Full schedules: [[04_Dossiers/Public_Accounts/Cabinet_DM_Public_Accounts_Layout|{p['stem']} Public Accounts Breakdown]]\n"
        )
        open(p["path"], "w", encoding="utf-8").write(body + new_sec)
        updated_profiles += 1

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines).strip() + "\n")

    print(f"WROTE {OUT_PATH} & UPDATED {updated_profiles} PROFILES")

if __name__ == "__main__":
    main()
