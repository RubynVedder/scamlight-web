#!/usr/bin/env python3
"""Erzeugt app/src/main/assets/vz_fakeshops.txt aus den öffentlichen Fake-Shop-Warnungen der Verbraucherzentralen
(warnung.fakeshop-finder.de, aktuelle Seite + Monatsarchive). D-081.

Nur Einträge, bei denen direkt über der Domain ein Datum steht (so ist jede Warnung auf der Seite aufgebaut).
Domains, die in der Liste bekannter Seiten (Majestic) stehen, werden NICHT übernommen, sondern gemeldet –
sie könnten echte Firmen sein, deren Name missbraucht wird. Vor jedem Release neu erzeugen.

Aufruf: python3 scripts/build_vz_list.py [Monate zurück, Standard 4] [Ausgabedatei] [known_domains.bin]
(Die tägliche Aktualisierung auf scamlight.de ruft es mit Ausgabedatei listen/vz_fakeshops.txt auf, D-084.)
"""

import datetime
import html
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "app", "src", "main", "assets", "vz_fakeshops.txt")
BASE = "https://warnung.fakeshop-finder.de/"
DATE = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")
DOMAIN = re.compile(r"^(?:https?://)?(?:www\.)?([a-z0-9äöüß-]+(?:\.[a-z0-9äöüß-]+)+)/?$", re.I)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "ScamLight-Listenbau/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def entries(page):
    text = html.unescape(re.sub(r"<[^>]+>", "\n", page))
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for prev, line in zip(lines, lines[1:]):
        m = DOMAIN.match(line)
        if DATE.match(prev) and m:
            yield m.group(1).lower(), prev


def main():
    months = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    out = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else OUT
    kpath = os.path.abspath(sys.argv[3]) if len(sys.argv) > 3 else os.path.join(
        ROOT, "app", "src", "main", "assets", "known_domains.bin"
    )
    today = datetime.date.today()
    urls = [BASE]
    y, m = today.year, today.month
    for _ in range(months):
        urls.append(f"{BASE}{y}_{m:02d}_warnungen.html")
        y, m = (y, m - 1) if m > 1 else (y - 1, 12)
    found = {}
    for url in urls:
        try:
            for dom, date in entries(fetch(url)):
                found.setdefault(dom, date)
        except urllib.error.HTTPError as e:
            print(f"  {url}: HTTP {e.code} (übersprungen)")
    known = set()
    if os.path.exists(kpath):
        import hashlib
        import struct

        data = open(kpath, "rb").read()
        known = set(struct.unpack(f">{len(data) // 4}i", data))

        def is_known(d):
            return struct.unpack(">i", hashlib.sha256(d.encode()).digest()[:4])[0] in known
    else:

        def is_known(d):
            return False

    skipped = sorted(d for d in found if is_known(d))
    keep = sorted(d for d in found if d not in skipped)
    if len(found) < 50:
        sys.exit(f"Nur {len(found)} Einträge gefunden – Seite geändert? Alte Liste bleibt.")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"# Fake-Shop-Warnungen der Verbraucherzentralen ({BASE}), Stand {today.isoformat()}\n")
        f.write("# Erzeugt mit scripts/build_vz_list.py – nicht von Hand bearbeiten.\n")
        f.writelines(d + "\n" for d in keep)
    print(f"{len(keep)} Domains → {out}")
    if skipped:
        print("NICHT übernommen (stehen in der Liste bekannter Seiten – bitte von Hand prüfen):", ", ".join(skipped))


if __name__ == "__main__":
    main()
