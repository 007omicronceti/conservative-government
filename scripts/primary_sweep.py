import os, re, glob, subprocess, urllib.request as ur, urllib.parse as up

UA = {"User-Agent": "Mozilla/5.0"}
IDX = "https://www.leg.bc.ca/about/accountability/members-disclosures/public-disclosure-statements"
PD, TD = "quartz/static/sources/Primary_Records/PDS", "content/05_Primary_Sources/PDS"
os.makedirs(PD, exist_ok=True); os.makedirs(TD, exist_ok=True)

h = ur.urlopen(ur.Request(IDX, headers=UA), timeout=25).read().decode("utf-8", "ignore")
pdfs = sorted(set(re.findall(r'href=["\'](/parliamentary-documents/[^"\']+\.pdf[^"\']*)["\']', h, re.I)))
cab = [os.path.basename(p)[:-3] for p in sorted(glob.glob("content/02_Cabinet/*.md"))]
ok = 0

for href in pdfs:
    raw = "https://lims.leg.bc.ca/pdms/file/" + href.split("/parliamentary-documents/", 1)[1].replace(" ", "%20")
    base = up.unquote(os.path.basename(href.split("?")[0]))
    low, m = base.lower(), None
    for c in cab:
        f, l = c.split("_")[0].lower(), c.split("_")[-1].lower()
        if re.search(rf'(^|[^a-z]){re.escape(l)}([^a-z]|$)', low):
            if l == "neufeld" and not (f in low or f"neufeld, {f[0]}" in low): continue
            m = c; break
    if not m: continue
    sf = re.sub(r'[^A-Za-z0-9._-]+', '_', base)
    pp = f"{PD}/{m}__{sf}"
    try:
        d = ur.urlopen(ur.Request(raw, headers=UA), timeout=25).read()
        if not d.startswith(b"%PDF"): print("SKIP", sf); continue
        open(pp, "wb").write(d)
        t = subprocess.check_output(["pdftotext", "-layout", pp, "-"], stderr=subprocess.DEVNULL).decode("utf-8", "ignore").strip()
        open(f"{TD}/{m}__{sf[:-4]}.md", "w").write(f"---\ntitle: \"{m.replace('_',' ')} — {base}\"\ndate: 2026-11-20\ntags: [coi, pds, {m.lower()}]\n---\n\n# {m.replace('_',' ')} — {base}\n- [[02_Cabinet/{m}]] | [PDF](/static/sources/Primary_Records/PDS/{m}__{sf})\n\n```text\n{t}\n```\n")
        ok += 1; print(f"OK {len(d)//1024:3d}KB {len(t.split()):3d}w | {m}__{sf}")
    except Exception as e:
        print("ERR", sf, e)

print(f"\nDONE: {ok} REAL PDFs UNPACKED")
