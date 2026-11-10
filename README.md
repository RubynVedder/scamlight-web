# scamlight.de

Webseite der Android-App ScamLight (Impressum, Datenschutz) und die täglich aktualisierte Liste
`listen/vz_fakeshops.txt` (Fake-Shop-Warnungen der Verbraucherzentralen, Quelle: warnung.fakeshop-finder.de).

Die Seiten werden im App-Projekt mit `python3 scripts/build_site.py ~/scamlight-web` erzeugt – hier nicht von
Hand bearbeiten. Die Liste aktualisiert `.github/workflows/listen-aktualisieren.yml` jeden Tag automatisch.

## Quellen und Lizenzen
- Fake-Shop-Warnungen: Verbraucherzentralen, https://warnung.fakeshop-finder.de/
- `tools/known_domains.bin`: Hash-Werte aus der Majestic Million (CC BY 3.0, https://majestic.com)
- Kontakt: kontakt@scamlight.de · Impressum: https://scamlight.de/impressum/
