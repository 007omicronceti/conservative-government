import glob, os, re, unicodedata

TXT_PATH = "data_cache/pa_2025_26.txt"
OUT_PATH = "content/04_Dossiers/Public_Accounts/Cabinet_DM_Public_Accounts_Sweep.md"

def clean_dots(s: str) -> str:
    return re.sub(r"\s*\.{3,}\s*", " | ", s).strip()

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
                    "role": role,
                    "full": full,
                    "first": first,
                    "last": last,
                })
    return profiles

def line_matches_profile(raw_line: str, p: dict) -> bool:
    nln = norm_words(raw_line)
    if not nln:
        return False
    if p["full"] and p["full"] in nln:
        return True
    # Also check "LAST, FIRST" or "LAST, F" formatted entries
    for m in re.finditer(rf"\b{re.escape(p['last'])}\b\s*,?\s*([a-z0-9]+)", nln):
        given = m.group(1)
        if given == p["first"] or (len(given) == 1 and given == p["first"][0]):
            return True
    return False

def main():
    if not os.path.exists(TXT_PATH):
        raise SystemExit(f"Missing {TXT_PATH}; run pdftotext first.")

    raw_text = open(TXT_PATH, encoding="utf-8", errors="replace").read()
    pages = raw_text.split("\x0c")
    profiles = load_profiles()

    hits_by_stem = {p["stem"]: [] for p in profiles}

    for pno, page_txt in enumerate(pages, start=1):
        lines = [clean_dots(ln) for ln in page_txt.splitlines() if ln.strip()]
        for lno, ln in enumerate(lines):
            if not ln:
                continue
            for p in profiles:
                if line_matches_profile(ln, p):
                    ctx_start = max(0, lno - 1)
                    ctx_end = min(len(lines), lno + 3)
                    snippet = " // ".join(lines[ctx_start:ctx_end])
                    hits_by_stem[p["stem"]].append((pno, snippet))

    matched_profiles = [p for p in profiles if hits_by_stem[p["stem"]]]
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    out_lines = [
        "# B.C. Public Accounts 2025/26 Sweep — Cabinet & Deputy Ministers",
        "",
        f"- **Source:** `pa-2025-26-crf-detailed-schedules-of-payments.pdf` ({len(pages)} pages extracted)",
        f"- **Profiles Scanned:** {len(profiles)} (`02_Cabinet` + `03_Deputy_Ministers`)",
        f"- **Matched Profiles:** {len(matched_profiles)} / {len(profiles)}",
        "",
    ]

    for p in matched_profiles:
        recs = hits_by_stem[p["stem"]]
        print(f"  [PA 2025/26] {p['stem']} ({p['role']}): {len(recs)} matches")
        out_lines.append(f"### {p['stem']} ({p['role']}) — {len(recs)} matches")
        seen = set()
        shown = 0
        for pno, snip in recs:
            key = (pno, snip[:140])
            if key in seen:
                continue
            seen.add(key)
            out_lines.append(f"- **p.{pno}:** {snip[:360]}")
            shown += 1
            if shown >= 20:
                out_lines.append(f"- *...and {len(recs) - shown} more matches*")
                break
        out_lines.append("")

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines).strip() + "\n")

    print(f"WROTE {OUT_PATH} (matched={len(matched_profiles)}/{len(profiles)})")

if __name__ == "__main__":
    main()
