import glob, os, re, unicodedata

LAYOUT_TXT = "data_cache/pa_2025_26_layout.txt"
OUT_PATH = "content/04_Dossiers/Public_Accounts/PDS_Entity_Public_Accounts_CrossCheck.md"
NUM_RE = re.compile(r"\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b")

# High-specificity entities to match against PA 2025/26 schedules
TARGET_ENTITIES = [
    ("Cenovus Energy Inc.", "cenovus energy", ["Gavin_Dew", "Trevor_Halford"]),
    ("Open Text Corporation", "open text", ["Anna_Kindy"]),
    ("Rogers Communications Inc.", "rogers communications", ["Gavin_Dew"]),
    ("TD Canada Trust", "td canada trust", ["Kiel_Giddens"]),
    ("Tolko Industries Ltd.", "tolko industries", ["Ward_Stamer"]),
    ("Tourmaline Oil Corp.", "tourmaline oil", ["Anna_Kindy", "Gavin_Dew"]),
    ("Zoom Communications, Inc.", "zoom communications", ["Gavin_Dew"]),
]

def norm_txt(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s.lower())).strip()

def main():
    pages = open(LAYOUT_TXT, encoding="utf-8", errors="replace").read().split("\x0c")
    hits_by_stem = {}
    out_lines = [
        "# PDS Disclosed Entities vs. B.C. Public Accounts 2025/26 Cross-Check",
        "",
        f"- **Source Schedule Text:** `{LAYOUT_TXT}`",
        f"- **High-Signal Entities Tracked:** {len(TARGET_ENTITIES)}",
        "",
    ]

    for label, needle, stems in TARGET_ENTITIES:
        matches = []
        for pno, pg in enumerate(pages, start=1):
            lines = [re.sub(r"\s*\.{3,}\s*", "  ", ln).strip() for ln in pg.splitlines() if ln.strip()]
            sec = ""
            for ln in lines[:8]:
                if re.search(r"(SCHEDULE|TRANSFER|SUPPLIER|GRANT|CONTRIBUTION|PAYMENTS)", ln, re.I):
                    sec = re.sub(r"\s{2,}", " — ", ln)[:85]
                    break
            for ln in lines:
                nln = norm_txt(ln)
                if needle in nln:
                    amts = NUM_RE.findall(ln)
                    row_clean = re.sub(r"\s{2,}", " | ", ln)
                    matches.append((pno, sec, row_clean, amts))

        out_lines.append(f"### {label} (`{needle}`)")
        out_lines.append(f"- **Associated Profiles:** {', '.join(stems)}")
        if not matches:
            out_lines.append("- **Public Accounts 2025/26:** No matches found")
        else:
            seen = set()
            for pno, sec, row_clean, amts in matches:
                key = (pno, row_clean[:120])
                if key in seen:
                    continue
                seen.add(key)
                sec_tag = f" *[{sec}]*" if sec else ""
                amt_tag = f" — **Amounts:** `{' , '.join(amts)}`" if amts else ""
                bullet = f"- **p.{pno}**{sec_tag}: `{row_clean[:210]}`{amt_tag}"
                out_lines.append(bullet)
                for st in stems:
                    hits_by_stem.setdefault(st, []).append(f"- **{label}** (p.{pno}{', ' + sec if sec else ''}): `{row_clean[:180]}`{amt_tag}")
        out_lines.append("")

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines).strip() + "\n")

    linked = 0
    for folder in ("content/02_Cabinet/*.md", "content/03_Deputy_Ministers/*.md"):
        for path in sorted(glob.glob(folder)):
            stem = os.path.basename(path)[:-3]
            raw = open(path, encoding="utf-8").read()
            body = re.split(r"\n## PDS Entity Cross-Check[^\n]*", raw, maxsplit=1)[0].rstrip()
            if stem in hits_by_stem:
                sec_block = (
                    "\n\n## PDS Entity Cross-Check (Public Accounts 2025/26)\n"
                    + "\n".join(hits_by_stem[stem])
                    + "\n- Cross-check index: [[04_Dossiers/Public_Accounts/PDS_Entity_Public_Accounts_CrossCheck|PDS Entity Public Accounts Cross-Check]]\n"
                )
                open(path, "w", encoding="utf-8").write(body + sec_block)
                linked += 1
            elif body != raw.rstrip():
                open(path, "w", encoding="utf-8").write(body + "\n")

    print(f"WROTE {OUT_PATH} & LINKED {linked} PROFILES")

if __name__ == "__main__":
    main()
