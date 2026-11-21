import glob, html, os, re, time, urllib.parse, urllib.request, unicodedata

FRSEARCH_URL = "https://contributions.electionsbc.gov.bc.ca/pcs/frsearch.aspx"
CACHE_DIR = "data_cache/ebc_frsearch"
OUT_PATH = "content/04_Dossiers/Elections_BC/FRSearch_Sweep.md"

def norm_name(s: str) -> str:
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
                profiles.append({
                    "stem": stem,
                    "path": path,
                    "role": role,
                    "first": parts[0],
                    "last": " ".join(parts[1:]),
                    "norm_full": norm_name(" ".join(parts)),
                })
    return profiles

def extract_hidden_fields(page_html: str) -> dict[str, str]:
    fields = {}
    for m in re.finditer(r'<input[^>]+type=["\']hidden["\'][^>]*>', page_html, flags=re.I):
        tag = m.group(0)
        name_m = re.search(r'name=["\']([^"\']+)["\']', tag, flags=re.I)
        if not name_m:
            continue
        val_m = re.search(r'value=["\']([^"\']*)["\']', tag, flags=re.I)
        fields[name_m.group(1)] = html.unescape(val_m.group(1)) if val_m else ""
    return fields

def find_search_inputs(page_html: str) -> tuple[str | None, str | None]:
    txt_name = None
    btn_name = None
    for m in re.finditer(r'<input[^>]+>', page_html, flags=re.I):
        tag = m.group(0)
        t_m = re.search(r'type=["\']([^"\']+)["\']', tag, flags=re.I)
        n_m = re.search(r'name=["\']([^"\']+)["\']', tag, flags=re.I)
        if not n_m:
            continue
        itype = (t_m.group(1) if t_m else "text").lower()
        iname = n_m.group(1)
        if itype in ("text", "search") and txt_name is None:
            if re.search(r"(filer|name|search|candidate)", iname, re.I):
                txt_name = iname
        elif itype in ("submit", "image") and btn_name is None:
            if re.search(r"(search|submit|find|btn)", iname, re.I):
                btn_name = iname
    return txt_name, btn_name

def parse_result_rows(res_html: str, norm_full: str, last_norm: str, first_initial: str) -> list[str]:
    clean = re.sub(r"<script.*?</script>|<style.*?</style>", " ", res_html, flags=re.S | re.I)
    rows_out = []
    for tr_m in re.finditer(r"<tr[^>]*>(.*?)</tr>", clean, flags=re.S | re.I):
        tr_html = tr_m.group(1)
        cells = [
            re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", c))).strip()
            for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr_html, flags=re.S | re.I)
        ]
        cells = [c for c in cells if c]
        if len(cells) < 2:
            continue
        joined = " | ".join(cells[:8])
        if "(ALL)" in joined or joined.lower().count("(all)") >= 2:
            continue
        blob = norm_name(joined)
        if last_norm and re.search(rf"\b{re.escape(last_norm)}\b", blob):
            # Accept if full name matches or surname + first initial appears in the row
            first_tok = norm_full.split()[0] if norm_full.split() else ""
            if (first_tok and re.search(rf"\b{re.escape(first_tok)}", blob)) or (
                first_initial and re.search(rf"\b{re.escape(first_initial)}[a-z']*", blob)
            ):
                rows_out.append(joined)
    return rows_out[:15]

def main():
    profiles = load_profiles()
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/124.0 Mobile Safari/537.36",
    }

    init_html = ""
    live_ok = False
    try:
        req = urllib.request.Request(FRSEARCH_URL, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            init_html = resp.read().decode("utf-8", errors="replace")
        live_ok = True
    except Exception as exc:
        print(f"Live GET failed ({exc}); using cached surname responses where available.")

    hidden = extract_hidden_fields(init_html) if live_ok else {}
    txt_field, btn_field = find_search_inputs(init_html) if live_ok else (None, None)

    results_by_stem: dict[str, list[str]] = {}
    queried = 0
    errors = 0

    for p in profiles:
        last_surname = p["last"].split()[-1]
        last_norm = norm_name(last_surname)
        first_initial = norm_name(p["first"])[:1]

        # Check existing full-name cache first
        full_cache = os.path.join(CACHE_DIR, f"{p['stem']}.html")
        sur_cache = os.path.join(CACHE_DIR, f"sur_{last_norm}.html")

        matches = []
        if os.path.exists(full_cache):
            full_html = open(full_cache, encoding="utf-8", errors="replace").read()
            matches = parse_result_rows(full_html, p["norm_full"], last_norm, first_initial)

        if not matches:
            sur_html = ""
            if os.path.exists(sur_cache):
                sur_html = open(sur_cache, encoding="utf-8", errors="replace").read()
            elif live_ok and txt_field:
                queried += 1
                payload = dict(hidden)
                payload[txt_field] = last_surname
                if btn_field:
                    payload[btn_field] = "Search"
                data = urllib.parse.urlencode(payload).encode("utf-8")
                try:
                    req = urllib.request.Request(FRSEARCH_URL, data=data, headers=headers)
                    with urllib.request.urlopen(req, timeout=20) as resp:
                        sur_html = resp.read().decode("utf-8", errors="replace")
                    with open(sur_cache, "w", encoding="utf-8") as cf:
                        cf.write(sur_html)
                    time.sleep(0.35)
                except Exception as exc:
                    errors += 1
                    print(f"  [FRSearch surname] {p['stem']} error: {exc}")

            if sur_html:
                matches = parse_result_rows(sur_html, p["norm_full"], last_norm, first_initial)

        if matches:
            results_by_stem[p["stem"]] = matches

    out_lines = [
        "# Elections BC Financial Reports (`FRSearch.aspx`) Sweep",
        "",
        f"- **Endpoint:** `{FRSEARCH_URL}`",
        f"- **Profiles Scanned:** {len(profiles)}",
        f"- **Surname Fallback Queries Sent:** {queried} | **Request Errors:** {errors}",
        f"- **Profiles with Matched Report Rows:** {len(results_by_stem)} / {len(profiles)}",
        "",
    ]

    linked = 0
    for p in profiles:
        hits = results_by_stem.get(p["stem"], [])
        raw = open(p["path"], encoding="utf-8").read()
        body = re.split(r"\n## Elections BC Financial Reports[^\n]*", raw, maxsplit=1)[0].rstrip()

        if hits:
            out_lines.append(f"### {p['stem']} ({p['role']}) — {len(hits)} row(s)")
            for h in hits:
                out_lines.append(f"- `{h[:220]}`")
            out_lines.append("")

            sec = (
                "\n\n## Elections BC Financial Reports (FRSearch)\n"
                f"- Matched `FRSearch.aspx` rows: **{len(hits)}**\n"
                + "\n".join(f"- {h[:200]}" for h in hits[:5])
                + "\n- Full sweep: [[04_Dossiers/Elections_BC/FRSearch_Sweep|Elections BC FRSearch Sweep]]\n"
            )
            open(p["path"], "w", encoding="utf-8").write(body + sec)
            linked += 1
        elif body != raw.rstrip():
            open(p["path"], "w", encoding="utf-8").write(body + "\n")

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines).strip() + "\n")

    print(f"WROTE {OUT_PATH} | MATCHED {len(results_by_stem)}/{len(profiles)} PROFILES | LINKED {linked}")

if __name__ == "__main__":
    main()
