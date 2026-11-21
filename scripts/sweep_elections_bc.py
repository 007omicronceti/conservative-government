import glob, html, os, re, time, unicodedata, urllib.parse, urllib.request
from http.cookiejar import CookieJar

BASE = "https://contributions.electionsbc.gov.bc.ca/pcs/"
PAGES = ["SA1ASearch.aspx", "SA1Search.aspx"]

def norm_words(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s.lower())).strip()

def get_opener():
    cj = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [("User-Agent", "Mozilla/5.0")]
    return opener

def extract_form_state(page_html: str) -> dict[str, str]:
    payload = {}
    for m in re.finditer(r"<input\b[^>]*>", page_html, flags=re.I):
        tag = m.group(0)
        if re.search(r'type=["\']?hidden', tag, flags=re.I):
            nm = re.search(r'name=["\']([^"\']+)["\']', tag, flags=re.I)
            vl = re.search(r'value=["\']([^"\']*)["\']', tag, flags=re.I)
            if nm:
                payload[html.unescape(nm.group(1))] = html.unescape(vl.group(1)) if vl else ""

    for m in re.finditer(r"<select\b[^>]*name=[\"']([^\"']+)[\"'][^>]*>(.*?)</select>", page_html, flags=re.S | re.I):
        sname, body = html.unescape(m.group(1)), m.group(2)
        sel = re.search(r'<option[^>]*selected[^>]*value=["\']([^"\']*)["\']', body, flags=re.I)
        first = re.search(r'<option[^>]*value=["\']([^"\']*)["\']', body, flags=re.I)
        payload[sname] = html.unescape((sel or first).group(1)) if (sel or first) else "0"
    return payload

def load_profiles():
    profiles = []
    for folder in ("content/02_Cabinet/*.md", "content/03_Deputy_Ministers/*.md"):
        for path in sorted(glob.glob(folder)):
            stem = os.path.basename(path)[:-3]
            parts = [p for p in stem.split("_") if p and len(p) > 1]
            if len(parts) >= 2:
                first_last = " ".join(parts)
                last_first = f"{parts[-1]}, {' '.join(parts[:-1])}"
                profiles.append({
                    "stem": stem,
                    "first": norm_words(parts[0]),
                    "last": norm_words(parts[-1]),
                    "full": norm_words(first_last),
                    "queries": [first_last, last_first],
                })
    return profiles

def parse_grid_rows(resp_html: str, prof: dict) -> tuple[list[str], list[str], str]:
    # Extract summary banner if present
    tot_m = re.search(r"(Total For This Search:\s*\$[0-9,\.]+)", resp_html, flags=re.I)
    rec_m = re.search(r"(Records\s+\d+\s+to\s+\d+\s+of\s+\d+)", resp_html, flags=re.I)
    meta = " | ".join(x.group(1) for x in (tot_m, rec_m) if x)

    # Extract grid rows (tables with 5+ columns and a dollar amount or date)
    headers = []
    matched_rows = []
    for tbl in re.findall(r"<table\b[^>]*>(.*?)</table>", resp_html, flags=re.S | re.I):
        trs = re.findall(r"<tr\b[^>]*>(.*?)</tr>", tbl, flags=re.S | re.I)
        if len(trs) < 2:
            continue
        first_cells = [
            re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c)).strip()
            for c in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", trs[0], flags=re.S | re.I)
        ]
        if "Contributor Name" not in first_cells:
            continue
        headers = [c for c in first_cells if c]
        for tr in trs[1:]:
            if "Page$" in tr:
                continue
            cells = [
                re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c)).strip()
                for c in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", tr, flags=re.S | re.I)
            ]
            if len(cells) < 4:
                continue
            contrib_norm = norm_words(cells[0])
            # Match exact full name OR exact last name + exact first name token
            tokens = set(contrib_norm.split())
            if prof["full"] in contrib_norm or (prof["last"] in tokens and prof["first"] in tokens):
                matched_rows.append(" | ".join(cells))
    return headers, matched_rows, meta

def main():
    opener = get_opener()
    profiles = load_profiles()
    out_dir = "content/04_Dossiers/Elections_BC"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Cabinet_DM_Elections_BC_Sweep.md")

    lines = [
        "# Elections BC Provincial Contributions Sweep — Cabinet & Deputy Ministers",
        "",
        f"Profiles queried: **{len(profiles)}** (`02_Cabinet` + `03_Deputy_Ministers`)",
        "",
    ]

    for page in PAGES:
        url = BASE + page
        print(f"Fetching base form from {url} ...")
        init_html = opener.open(url, timeout=30).read().decode("utf-8", errors="replace")
        base_form = extract_form_state(init_html)

        sec_lines = [f"## {page}", ""]
        matched_profiles = 0
        captured_headers = []

        for prof in profiles:
            seen_rows = []
            seen_set = set()
            last_meta = ""

            for q in prof["queries"]:
                payload = dict(base_form)
                payload["ctl00$ContentPlaceHolder1$txtContributor"] = q
                payload["ctl00$ContentPlaceHolder1$cmdSearchResult"] = "Search"
                data = urllib.parse.urlencode(payload).encode("utf-8")

                try:
                    resp_html = opener.open(url, data=data, timeout=30).read().decode("utf-8", errors="replace")
                except Exception as e:
                    print(f"  [{page}] {q}: ERROR {e}")
                    continue

                hdrs, rows, meta = parse_grid_rows(resp_html, prof)
                if hdrs and not captured_headers:
                    captured_headers = hdrs
                if meta:
                    last_meta = meta
                for r in rows:
                    if r not in seen_set:
                        seen_set.add(r)
                        seen_rows.append(r)

                # Follow ASP.NET grid pagination if present (Page$2 .. Page$10)
                page_targets = re.findall(
                    r"__doPostBack\('([^']+)','(Page\$\d+)'\)", resp_html
                )
                cur_html = resp_html
                visited_pages = {"Page$1"}
                for target, arg in page_targets:
                    if arg in visited_pages:
                        continue
                    visited_pages.add(arg)
                    pg_payload = extract_form_state(cur_html)
                    pg_payload["__EVENTTARGET"] = target
                    pg_payload["__EVENTARGUMENT"] = arg
                    try:
                        cur_html = opener.open(
                            url, data=urllib.parse.urlencode(pg_payload).encode("utf-8"), timeout=30
                        ).read().decode("utf-8", errors="replace")
                        _, more_rows, _ = parse_grid_rows(cur_html, prof)
                        for r in more_rows:
                            if r not in seen_set:
                                seen_set.add(r)
                                seen_rows.append(r)
                    except Exception:
                        break
                    time.sleep(0.2)

                time.sleep(0.25)

            if seen_rows:
                matched_profiles += 1
                # Sum exact matched dollar amounts
                total_amt = 0.0
                for r in seen_rows:
                    for amt in re.findall(r"\$([0-9,]+\.\d{2})", r):
                        total_amt += float(amt.replace(",", ""))
                print(f"  [{page}] {prof['stem']}: {len(seen_rows)} exact rows (${total_amt:,.2f})")
                sec_lines.append(
                    f"### {prof['stem']} — {len(seen_rows)} exact rows (${total_amt:,.2f})"
                )
                if last_meta:
                    sec_lines.append(f"- Query meta: `{last_meta}`")
                for cr in seen_rows:
                    sec_lines.append(f"- {cr}")
                sec_lines.append("")

        sec_lines.insert(1, f"- Matched profiles: **{matched_profiles}** / {len(profiles)}")
        if captured_headers:
            sec_lines.insert(2, f"- Columns: `{' | '.join(captured_headers)}`")
        lines.extend(sec_lines)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).strip() + "\n")
    print(f"WROTE {out_path}")

if __name__ == "__main__":
    main()
