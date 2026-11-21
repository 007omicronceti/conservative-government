import csv, glob, io, os, re, unicodedata, urllib.request, zipfile

BASE = "https://www.lobbyistsregistrar.bc.ca/app/secure/orl/lrs/do/mssDtstRprt?file="
DATASETS = {
    "registrations": BASE + "ORL_Registration_Data.zip",
    "lars": BASE + "ORL_LAR_Data.zip",
}

def norm_words(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s.lower())).strip()

def load_profiles():
    profiles = []
    for folder in ("content/02_Cabinet/*.md", "content/03_Deputy_Ministers/*.md"):
        for path in sorted(glob.glob(folder)):
            stem = os.path.basename(path)[:-3]
            parts = [p for p in stem.split("_") if p and len(p) > 1]
            if len(parts) >= 2:
                full = norm_words(" ".join(parts))
                last = norm_words(parts[-1])
                first = norm_words(parts[0])
                profiles.append({
                    "stem": stem,
                    "path": path,
                    "full": full,
                    "first": first,
                    "last": last,
                })
    return profiles

def fetch_zip(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()

def scan_csv_bytes(data: bytes, source_name: str, profiles: list[dict]):
    hits_by_stem = {p["stem"]: [] for p in profiles}
    total_rows = 0
    headers_seen = []

    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        for member in zf.namelist():
            if not member.lower().endswith(".csv"):
                continue
            with zf.open(member) as raw_f:
                text_f = io.TextIOWrapper(raw_f, encoding="utf-8-sig", errors="replace", newline="")
                reader = csv.DictReader(text_f)
                if reader.fieldnames and not headers_seen:
                    headers_seen = list(reader.fieldnames)
                for row in reader:
                    total_rows += 1
                    blob = norm_words(" ".join(str(v or "") for v in row.values()))
                    for p in profiles:
                        # Require full name OR last name + first initial/word in row blob
                        if p["full"] in blob or (
                            len(p["last"]) >= 4
                            and re.search(rf"\b{re.escape(p['last'])}\b", blob)
                            and re.search(rf"\b{re.escape(p['first'][0])}[a-z]*\b", blob)
                        ):
                            hits_by_stem[p["stem"]].append((member, row))

    return total_rows, headers_seen, hits_by_stem

def main():
    profiles = load_profiles()
    out_dir = "content/04_Dossiers/Lobbying_ORL"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Cabinet_DM_ORL_Sweep.md")

    lines = [
        "# B.C. ORL Lobbying Sweep — Cabinet & Deputy Ministers",
        "",
        f"Profiles scanned: **{len(profiles)}** (`02_Cabinet` + `03_Deputy_Ministers`)",
        "",
    ]

    for key, url in DATASETS.items():
        print(f"Downloading {key} from {url} ...")
        blob = fetch_zip(url)
        rows, headers, hits = scan_csv_bytes(blob, key, profiles)
        matched_stems = [k for k, v in hits.items() if v]
        print(f"[{key}] rows={rows} | matched_profiles={len(matched_stems)}")
        lines.append(f"## {key.upper()}")
        lines.append(f"- Rows scanned: **{rows}**")
        lines.append(f"- Matched profiles: **{len(matched_stems)}**")
        if headers:
            lines.append(f"- Sample columns: `{'`, `'.join(headers[:8])}`")
        lines.append("")
        for stem in matched_stems:
            recs = hits[stem]
            lines.append(f"### {stem} ({len(recs)} row matches)")
            for member, row in recs[:15]:
                compact = " | ".join(
                    f"{k}: {str(v).strip()}" for k, v in row.items() if v and str(v).strip()
                )
                lines.append(f"- `{member}` — {compact[:260]}")
            if len(recs) > 15:
                lines.append(f"- *...and {len(recs) - 15} more rows*")
            lines.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).strip() + "\n")
    print(f"WROTE {out_path}")

if __name__ == "__main__":
    main()
