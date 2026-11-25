import sys
from pathlib import Path

TARGETS = {
    "crd": "content/04_cariboo_chilcotin/crd-solid-waste-and-governance.md",
    "100m": "content/04_cariboo_chilcotin/district-of-100-mile-house-and-south-cariboo.md",
    "doerkson": "content/04_cariboo_chilcotin/lorne-doerkson-cariboo-chilcotin-links.md",
    "notes": "content/04_cariboo_chilcotin/south-cariboo-waste-and-infrastructure-notes.md",
}

def main():
    if len(sys.argv) < 4:
        print("Usage: append_note.py <crd|100m|doerkson|notes> <heading> <bullet1> [bullet2 ...]")
        sys.exit(1)
    key, heading, bullets = sys.argv[1], sys.argv[2], sys.argv[3:]
    path = Path(TARGETS[key])
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    header = f"## {heading}"
    if header in existing:
        print(f"Already present in {path}: {header}")
        return
    addition = "\n" + header + "\n" + "\n".join(f"- {b}" for b in bullets) + "\n"
    path.write_text(existing + addition, encoding="utf-8")
    print(f"Appended '{header}' to {path}")

if __name__ == "__main__":
    main()
