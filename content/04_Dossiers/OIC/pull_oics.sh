#!/usr/bin/env bash
OUT_DIR=~/Conservative_Government/03_Sources/OIC
INDEX_URL="https://www.bclaws.gov.bc.ca/civix/content/oic/oic_cur/2026/?xsl=/templates/browse.xsl"
echo "Fetching 2026 BC Laws OIC index..."
curl -sL "$INDEX_URL" -o "$OUT_DIR/oic_2026_index.html"
python3 - << 'PYEOF'
import os, re
path = os.path.expanduser("~/Conservative_Government/03_Sources/OIC/oic_2026_index.html")
html = open(path, encoding="utf-8", errors="ignore").read()
# Extract OIC numbers and titles from the 2026 browse page
matches = re.findall(r'href="([^"]*oic_cur/2026/[^"]*)"[^>]*>([^<]+)<', html)
if not matches:
    print("No OIC links parsed (BC Laws may require browser/JS or OICs not yet posted). Check:", path)
else:
    print(f"Found {len(matches)} OIC entries in 2026. Latest 15:")
    for url, title in matches[-15:]:
        print(f"  - {title.strip()} -> https://www.bclaws.gov.bc.ca{url}")
PYEOF
