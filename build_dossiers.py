import pathlib, re, subprocess

src = pathlib.Path("static/sources/Cariboo_Chilcotin")
out_dir = pathlib.Path("content/04_Dossiers/Cariboo_Chilcotin")

def clean_html(p):
    raw = p.read_text(errors="ignore")
    raw = re.sub(r"<(script|style|nav|header|footer|aside)[\s\S]*?</\1>", " ", raw, flags=re.I)
    txt = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", txt).strip()

def read_pdf(p):
    try:
        r = subprocess.run(["pdftotext", str(p), "-"], capture_output=True, text=True, timeout=20)
        return re.sub(r"\s+", " ", r.stdout).strip()
    except Exception as e:
        return f"[PDF error: {e}]"

texts = {}
for f in sorted(src.glob("*.*")):
    if f.suffix.lower() == ".html":
        texts[f.name] = clean_html(f)
    elif f.suffix.lower() == ".pdf":
        texts[f.name] = read_pdf(f)

def snippets(names, terms, limit=900):
    lines = []
    for n in names:
        t = texts.get(n, "")
        if not t:
            continue
        found = []
        for term in terms:
            m = re.search(re.escape(term), t, re.I)
            if m:
                s = max(0, m.start() - 180)
                e = min(len(t), m.end() + 420)
                found.append(t[s:e].strip())
        if found:
            lines.append(f"### Source: `{n}`\n" + "\n\n".join(f"> {x[:limit]}" for x in found[:2]))
        else:
            lines.append(f"### Source: `{n}` (excerpt)\n> {t[:500]}")
    return "\n\n".join(lines)

(out_dir / "Dossier_Cariboo_Gold_Project.md").write_text(
    "---\ntitle: Cariboo Gold Project (Wells) — Permitting, Labour & Compliance\ndate: 2026-11-20\ntags: [cariboo-chilcotin, mining, cariboo-gold, wells, barkerville, osisko, labour]\n---\n\n"
    "# Cariboo Gold Project (Wells)\n\n"
    "Extracted from local project and regional records in `static/sources/Cariboo_Chilcotin/`.\n\n"
    + snippets(["Cariboo_Gold_Strike_Mandate_CKPG_2026-11-16.html", "Cariboo_Gold_EAO_EPIC.html", "Cariboo_Gold_Osisko_Update_2026-10-27.html"], ["Wells", "strike", "UNITE HERE", "Barkerville", "Osisko", "certificate"])
    + "\n\n## Key Links\n- [[01_Ministries/08_Energy_Mines_and_Petroleum_Resources|Energy, Mines & Petroleum Resources]]\n- [[01_Ministries/15_Post-Secondary_Education_and_Labour|Post-Secondary Ed & Labour]]\n- [[01_Ministries/09_Environment|Environment]]\n"
)

(out_dir / "Dossier_DRIPA_Repeal_Cariboo_Title.md").write_text(
    "---\ntitle: DRIPA Repeal & Cariboo-Chilcotin Aboriginal Title\ndate: 2026-11-20\ntags: [cariboo-chilcotin, dripa, aboriginal-title, reconciliation, fnlc, hansard]\n---\n\n"
    "# DRIPA Repeal & Cariboo-Chilcotin Aboriginal Title\n\n"
    "Extracted from local Hansard and First Nations policy records in `static/sources/Cariboo_Chilcotin/`.\n\n"
    + snippets(["Hansard_2026-04-13_McInnis_DRIPA.html", "FNLC_2026_Election_Package_DRIPA.pdf"], ["DRIPA", "Declaration", "title", "reconciliation", "McInnis", "Tsilhqot"])
    + "\n\n## Key Links\n- [[01_Ministries/13_Indigenous_Relations_and_Reconciliation|MIRR]]\n- [[01_Ministries/03_Attorney_General|Attorney General]]\n- [[01_Ministries/01_Office_of_the_Premier|Office of the Premier]]\n"
)

(out_dir / "Dossier_Highway97_Cariboo_Connector.md").write_text(
    "---\ntitle: Highway 97 Cariboo Connector & Regional Infrastructure\ndate: 2026-11-20\ntags: [cariboo-chilcotin, transportation, highway-97, 100-mile-house, nclga]\n---\n\n"
    "# Highway 97 Cariboo Connector & Regional Infrastructure\n\n"
    "Extracted from local council agenda and NCLGA records in `static/sources/Cariboo_Chilcotin/`.\n\n"
    + snippets(["100_Mile_House_Council_Agenda_2026-10-13.pdf", "NCLGA_2026_Resolutions.html"], ["Highway 97", "97", "R19", "transportation", "100 Mile", "infrastructure"])
    + "\n\n## Key Links\n- [[01_Ministries/18_Transportation_and_Infrastructure|Transportation & Infrastructure]]\n- [[01_Ministries/10_Finance|Finance]]\n"
)

(out_dir / "Dossier_Wildfire_Chilcotin_Recovery.md").write_text(
    "---\ntitle: Wildfire Fuel Breaks & Chilcotin Landslide / Salmon Recovery\ndate: 2026-11-20\ntags: [cariboo-chilcotin, wildfire, bcws, chilcotin, salmon, emergency-management]\n---\n\n"
    "# Wildfire Fuel Breaks & Chilcotin Landslide / Salmon Recovery\n\n"
    "Extracted from local BC Wildfire Service and TNG records in `static/sources/Cariboo_Chilcotin/`.\n\n"
    + snippets(["BCWS_Watch_Lake_Fuel_Break_2026-11-03.html", "BCWS_Mirage_Lake_Fuel_Break_2026-11-03.html", "TNG_Chilcotin_Salmon_Task_Force_2026-08-18.pdf"], ["Watch Lake", "Mirage Lake", "100 Mile", "Chilcotin", "salmon", "landslide"])
    + "\n\n## Key Links\n- [[01_Ministries/16_Public_Safety_and_Solicitor_General|Public Safety & Solicitor General]]\n- [[01_Ministries/19_Water_Land_and_Natural_Resource_Operations|WLNRO]]\n- [[01_Ministries/02_Agriculture|Agriculture]]\n"
)

print("Generated 4 dossiers from local HTML/PDF files.")
