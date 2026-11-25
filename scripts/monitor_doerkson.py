import datetime, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path

OUT = Path("content/04_cariboo_chilcotin/doerkson-live-monitor.md")
FEEDS = [
    ("Office of the Premier", "https://news.gov.bc.ca/office-of-the-premier/feed"),
    ("Press (Lorne Doerkson)", "https://news.google.com/rss/search?q=Lorne+Doerkson&hl=en-CA&gl=CA&ceid=CA:en"),
]
def pull(url):
    try:
        r = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        root = ET.fromstring(urllib.request.urlopen(r, timeout=15).read())
        return [f"- **{i.findtext('pubDate','')}** — [{i.findtext('title','')}]({i.findtext('link','')})" for i in root.findall(".//item")[:15]]
    except Exception as e:
        return [f"- *Error: {e}*"]
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
lines = ["---", 'title: "Lorne Doerkson — Live Intel Monitor"', "---", "", f"*Compiled: **{now}***", ""]
for name, url in FEEDS:
    lines += [f"## {name}", *pull(url), ""]
OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {OUT}")
