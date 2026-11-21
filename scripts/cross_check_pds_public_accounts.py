import glob, os, re, unicodedata

PDS_DIR = "content/05_Primary_Sources/PDS"
LAYOUT_TXT = "data_cache/pa_2025_26_layout.txt"
OUT_PATH = "content/04_Dossiers/Public_Accounts/PDS_Entity_Public_Accounts_CrossCheck.md"

NUM_RE = re.compile(r"\$?\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?")
ENTITY_SUFFIX_RE = re.compile(
    r"\b[A-Z][A-Za-z0-9&'\-\.]*(?:\s+[A-Z0-9][A-Za-z0-9&'\-\.]*){0,6}\s+"
    r"(?:Inc\.?|Incorporated|Ltd\.?|Limited|Corp\.?|Corporation|Co\.?|Company|"
    r"LLP|LP|L\.P\.|Holdings?|Ventures?|Group|Partners?|Properties|Developments?|"
    r"Associates?|Consulting|Advisory|Society|Association|Foundation|Institute|"
    r"Council|Trust|Fund|Board|Authority|Enterprises?|Industries|Services)\b"
)

NOISE_EXACT = {
    "province of british columbia",
    "public accounts",
    "members compensation",
    "legislative assembly",
    "deputy ministers",
    "conflict of interest",
    "public disclosure",
    "disclosure statement",
    "british columbia",
    "government of british columbia",
}

def norm_entity(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"\b(inc|incorporated|ltd|limited|corp|corporation|co|company|llp|lp)\b\.?", " ", s.lower())
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def load_profile_stems() -> list[str]:
    stems = []
    for folder in ("content/02_Cabinet/*.md", "content/03_Deputy_Ministers/*.md"):
        for p in glob.glob(folder):
            stems.append(os.path.basename(p)[:-3])
    return sorted(set(stems), key=len, reverse=True)

def infer_profile(rel_path: str, text: str, stems: list[str]) -> str:
    blob = f"{rel_path} {text[:600]}".lower()
    for st in stems:
        human = st.replace("_", " ").lower()
        if st.lower() in blob or human in blob:
            return st
    return "Unassigned"

def extract_entities_from_pds(text: str) -> set[str]:
    found = set()
    # Clean markdown formatting markers while preserving line breaks
    cleaned = re.sub(r"[*_`#>\[\]\(\)]+", " ", text)
    for m in ENTITY_SUFFIX_RE.finditer(cleaned):
        cand = re.sub(r"\s+", " ", m.group(0)).strip(" ,;:-")
        ncand = norm_entity(cand)
        if len(ncand) >= 5 and ncand not in NOISE_EXACT:
            found.add(cand)

    # Also inspect bullet/table lines for entity-like labels
    for ln in cleaned.splitlines():
        s = ln.strip(" -•\t")
        if len(s) < 5 or len(s) > 120:
            continue
        if re.search(r"\b(inc|ltd|corp|llp|lp|holdings|ventures|society|association|foundation|group)\b", s, re.I):
            # Take clause before colon/pipe/dash if present
            head = re.split(r"\s+[:|–—-]\s+", s)[0].strip()
            nhead = norm_entity(head)
            if len(nhead) >= 5 and nhead not in NOISE_EXACT:
                found.add(head)
    return found

def main():
    if not os.path.exists(PDS_DIR):
        raise SystemExit(f"Missing PDS directory: {PDS_DIR}")
    if not os.path.exists(LAYOUT_TXT):
        raise SystemExit(f"Missing layout text: {LAYOUT_TXT}")

    stems = load_profile_stems()
    pds_files = sorted(
        p for p in glob.glob(f"{PDS_DIR}/**/*", recursive=True)
        if os.path.isfile(p) and os.path.splitext(p)[1].lower() in {".md", ".txt", ".csv"}
    )

    # Map normalized entity -> list of (profile, source_file, raw_entity)
    entity_sources: dict[str, list[tuple[str, str, str]]] = {}
    for fpath in pds_files:
        rel = os.path.relpath(fpath, ".")
        txt = open(fpath, encoding="utf-8", errors="replace").read()
        prof = infer_profile(rel, txt, stems)
        for raw_ent in extract_entities_from_pds(txt):
            nent = norm_entity(raw_ent)
            if nent:
                entity_sources.setdefault(nent, []).append((prof, rel, raw_ent))

    pages = open(LAYOUT_TXT, encoding="utf-8", errors="replace").read().split("\x0c")
    matches_by_ent: dict[str, list[tuple[int, str, str, list[str]]]] = {k: [] for k in entity_sources}

    for pno, pg in enumerate(pages, start=1):
        lines = [re.sub(r"\s*\.{3,}\s*", "  ", ln).strip() for ln in pg.splitlines() if ln.strip()]
        sec = ""
        for ln in lines[:8]:
            if re.search(r"(SCHEDULE|TRANSFER|SUPPLIER|GRANT|CONTRIBUTION|PAYMENTS|REMUNERATION)", ln, re.I):
                sec = re.sub(r"\s{2,}", " — ", ln)[:90]
                break

        for ln in lines:
            nln = norm_entity(ln)
            if len(nln) < 5:
                continue
            for nent in entity_sources:
                # Require full normalized entity substring or all significant tokens (len>=4) present
                toks = [t for t in nent.split() if len(t) >= 4]
                matched = False
                # Require at least 2 distinct words or >=10 chars so generic single words ("associates", "capital") don't flood
                sig_words = [w for w in nent.split() if len(w) >= 3]
                if len(sig_words) >= 2 and nent in nln:
                    matched = True
                elif len(sig_words) >= 2 and len(toks) >= 2 and all(re.search(rf"\b{re.escape(t)}\b", nln) for t in toks):
                    matched = True
                elif len(sig_words) == 1 and len(nent) >= 11 and nent in nln:
                    matched = True
                if matched:
                    amts = [a.strip() for a in NUM_RE.findall(ln)]
                    row_clean = re.sub(r"\s{2,}", " | ", ln)
                    matches_by_ent[nent].append((pno, sec, row_clean, amts))

    matched_ents = [nent for nent, hits in matches_by_ent.items() if hits]
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    out_lines = [
        "# PDS Disclosed Entities vs. B.C. Public Accounts 2025/26 Cross-Check",
        "",
        f"- **PDS Files Scanned:** {len(pds_files)} (`{PDS_DIR}`)",
        f"- **Distinct Entities Extracted:** {len(entity_sources)}",
        f"- **Entities Matched in Public Accounts 2025/26:** {len(matched_ents)}",
        "",
    ]

    for nent in sorted(matched_ents):
        srcs = entity_sources[nent]
        hits = matches_by_ent[nent]
        prof_list = sorted({p for p, _, _ in srcs})
        raw_names = sorted({r for _, _, r in srcs})
        out_lines.append(f"### {raw_names[0]} (`{nent}`)")
        out_lines.append(f"- **Profiles / Sources:** {', '.join(prof_list)} ({len(srcs)} PDS reference(s))")
        seen = set()
        shown = 0
        for pno, sec, row_clean, amts in hits:
            key = (pno, row_clean[:120])
            if key in seen:
                continue
            seen.add(key)
            sec_part = f" *[{sec}]*" if sec else ""
            amt_part = f" — **Amounts:** `{' , '.join(amts)}`" if amts else ""
            out_lines.append(f"- **p.{pno}**{sec_part}: `{row_clean[:220]}`{amt_part}")
            shown += 1
            if shown >= 15:
                out_lines.append(f"- *...and {len(hits) - shown} more schedule rows*")
                break
        out_lines.append("")

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines).strip() + "\n")

    print(f"SCANNED {len(pds_files)} PDS FILES | EXTRACTED {len(entity_sources)} ENTITIES | MATCHED {len(matched_ents)} IN PA 2025/26")
    print(f"WROTE {OUT_PATH}")

if __name__ == "__main__":
    main()
