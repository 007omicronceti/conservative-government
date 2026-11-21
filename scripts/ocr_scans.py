import os, glob, subprocess

PD = "quartz/static/sources/Primary_Records/PDS"
IMG = f"{PD}/images"
TD = "content/05_Primary_Sources/PDS"

targets = [
    "Korky_Neufeld__NEUFELD_KORKY_-_20Jan26.pdf",
    "Claire_Rattee__RATTEE_-_20Jan26.pdf",
]

for pdf in targets:
    pp = f"{PD}/{pdf}"
    stem = pdf[:-4]
    if not os.path.exists(pp): continue
    subprocess.run(["pdftoppm", "-png", "-r", "300", pp, f"{IMG}/{stem}"], check=True)
    imgs = sorted(glob.glob(f"{IMG}/{stem}-*.png"))
    ocr_txt, img_md = [], []
    for im in imgs:
        bn = os.path.basename(im)
        img_md.append(f"![{bn}](/static/sources/Primary_Records/PDS/images/{bn})")
        t = subprocess.check_output(["tesseract", im, "stdout", "--psm", "6"], stderr=subprocess.DEVNULL).decode("utf-8", "ignore").strip()
        ocr_txt.append(f"--- PAGE {bn} ---\n{t}")
    full_t = "\n\n".join(ocr_txt)
    md_p = f"{TD}/{stem}.md"
    cab = stem.split("__")[0]
    open(md_p, "w").write(f"---\ntitle: \"{cab.replace('_',' ')} — {stem.split('__',1)[1]} (OCR)\"\ndate: 2026-11-20\ntags: [coi, pds, ocr, {cab.lower()}]\n---\n\n# {cab.replace('_',' ')} — {stem.split('__',1)[1]}\n- [[02_Cabinet/{cab}]] | [PDF](/static/sources/Primary_Records/PDS/{pdf})\n\n## Scanned Pages\n" + "\n".join(img_md) + f"\n\n## Tesseract OCR Text\n```text\n{full_t}\n```\n")
    print(f"OCR OK | {len(imgs)} imgs | {len(full_t.split())}w | {stem}")
