# Hinweise für Claude

## Strafrecht-Nachschlagewerk (`gesetze/`)

Im Ordner `gesetze/` liegen die aktuellen Texte des deutschen Strafrechts als
Markdown (StGB, StPO, JGG, BtMG, KCanG, OWiG, StVG, GVG), geladen von
gesetze-im-internet.de. Die Action `.github/workflows/gesetze.yml` aktualisiert
sie monatlich; `gesetze/README.md` zeigt das Abrufdatum.

Wenn der Nutzer eine rechtliche Frage stellt (Strafrecht, Verfahren,
Ordnungswidrigkeiten, Verkehr, Drogen …):

1. **Erst nachschlagen, dann antworten.** Die einschlägigen Vorschriften in
   `gesetze/*.md` suchen, z. B. `grep -n "^## § 242 " gesetze/stgb.md` oder
   per Stichwort `grep -n -i "diebstahl" gesetze/stgb.md`, und den Abschnitt
   lesen. Nicht aus dem Gedächtnis zitieren.
2. **Mit Wortlaut belegen.** Paragraph, Absatz und Nummer nennen
   (z. B. „§ 243 Abs. 1 S. 2 Nr. 1 StGB“) und die entscheidende Stelle wörtlich
   zitieren. Den Stand angeben: die Zeilen „Stand:“ oben in der Gesetzesdatei
   (letzte berücksichtigte Änderung). Ist gesetze-im-internet.de für GitHub
   gesperrt, stammt der Text aus einer Archivkopie – deren Datum steht in der
   Zeile „Quelle:“. Bei älteren Kopien darauf hinweisen, dass sich seither
   etwas geändert haben kann.
3. **Wie ein Anwalt prüfen:** Tatbestand (objektiv/subjektiv), Rechtswidrigkeit,
   Schuld, Strafrahmen, mögliche Qualifikationen/Privilegierungen, Verjährung
   (§§ 78 ff. StGB), Strafantrag (§ 77 StGB), und verfahrensrechtlich:
   Rechte als Beschuldigter (§§ 136, 163a StPO: Schweigerecht, Anwalt),
   Einstellungsmöglichkeiten (§§ 153, 153a, 170 Abs. 2 StPO), Fristen.
4. **Einfach erklären**, auf Deutsch, verständlich für Laien.
5. **Grenzen offen sagen:** Das ist keine Rechtsberatung. Rechtsprechung,
   Kommentare und die Akte sind hier nicht enthalten. Bei einem echten
   Verfahren (Vorladung, Anhörungsbogen, Strafbefehl, Anklage) immer raten,
   vor jeder Aussage einen Fachanwalt für Strafrecht einzuschalten; auf Fristen
   hinweisen (z. B. Einspruch gegen Strafbefehl: 2 Wochen, § 410 StPO).

**Datenschutz:** Dieses Repository ist öffentlich (GitHub Pages). Keine
persönlichen Details zu Fällen, Namen oder Aktenzeichen in Dateien schreiben
oder committen – solche Angaben nur im Chat verwenden.

Fehlt ein Gesetz, den Slug von gesetze-im-internet.de in `GESETZE` in
`tools/gesetze_laden.py` ergänzen und pushen; die Action lädt es dann.
