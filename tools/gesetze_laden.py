#!/usr/bin/env python3
"""Lädt Gesetze von gesetze-im-internet.de (XML) und speichert sie als Markdown.

Aufruf:  python3 tools/gesetze_laden.py            # alle Gesetze aus GESETZE
         python3 tools/gesetze_laden.py stgb stpo  # nur bestimmte (Slugs)
         python3 tools/gesetze_laden.py --xml datei.xml  # lokale XML-Datei (Test)

Ergebnis: gesetze/<slug>.md, eine Datei pro Gesetz, jede Vorschrift als
Überschrift "## § 242 Diebstahl", damit sie per grep leicht zu finden ist.
"""
import datetime
import io
import socket
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

# Slug auf gesetze-im-internet.de -> Kurzbeschreibung
GESETZE = {
    "stgb": "Strafgesetzbuch",
    "stpo": "Strafprozessordnung",
    "jgg": "Jugendgerichtsgesetz",
    "btmg_1981": "Betäubungsmittelgesetz",
    "kcang": "Konsumcannabisgesetz",
    "owig_1968": "Gesetz über Ordnungswidrigkeiten",
    "stvg": "Straßenverkehrsgesetz",
    "gvg": "Gerichtsverfassungsgesetz",
}

ZIEL = Path(__file__).resolve().parent.parent / "gesetze"
URL = "https://www.gesetze-im-internet.de/{slug}/xml.zip"


def text_von(el):
    """Wandelt ein <Content>-Element in lesbaren Text mit Absätzen um."""
    teile = []
    EINZUG = "\x00"  # übersteht das Zusammenfassen von Leerraum

    def lauf(e, tiefe):
        if e.tag == "BR":
            teile.append("\n")
        elif e.tag == "P":
            teile.append("\n\n")
        elif e.tag == "DT":
            teile.append("\n" + EINZUG * 2 * tiefe + "- ")
        elif e.tag == "row":
            teile.append("\n")
        if e.text:
            teile.append(e.text.replace("\n", " "))
        for kind in e:
            lauf(kind, tiefe + (1 if e.tag == "DL" else 0))
            if kind.tail:
                teile.append(kind.tail.replace("\n", " "))
        if e.tag in ("DT", "LA"):
            teile.append(" ")
        elif e.tag == "entry":
            teile.append(" | ")

    lauf(el, -1)
    zeilen = [" ".join(z.split()).replace(EINZUG, " ")
              for z in "".join(teile).split("\n")]
    text = "\n".join(zeilen)
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text.strip()


def zu_markdown(xml_bytes, slug):
    root = ET.fromstring(xml_bytes)
    normen = root.findall("norm")
    if not normen:
        raise ValueError("keine <norm>-Elemente gefunden")

    kopf = normen[0].find("metadaten")
    titel = (kopf.findtext("langue") or GESETZE.get(slug, slug)).strip()
    abk = (kopf.findtext("jurabk") or slug.upper()).strip()
    stand = [" ".join((s.findtext("standkommentar") or "").split())
             for s in kopf.findall("standangabe")]

    out = [f"# {titel} ({abk})", ""]
    out.append(f"Quelle: https://www.gesetze-im-internet.de/{slug}/  ")
    out.append(f"Abgerufen: {datetime.date.today().isoformat()}")
    for s in stand:
        if s:
            out.append(f"- Stand: {s}")
    out.append("")

    for norm in normen[1:]:
        meta = norm.find("metadaten")
        inhalt = norm.find("textdaten/text/Content")
        enbez = " ".join((meta.findtext("enbez") or "").split())
        ntitel = " ".join("".join(meta.find("titel").itertext()).split()) \
            if meta.find("titel") is not None else ""
        gl = meta.find("gliederungseinheit")

        if not enbez and gl is not None:
            # Gliederungsüberschrift (Buch, Abschnitt, Titel ...)
            bez = " ".join((gl.findtext("gliederungsbez") or "").split())
            gtitel = " ".join("".join(gl.find("gliederungstitel").itertext()).split()) \
                if gl.find("gliederungstitel") is not None else ""
            out += [f"### {bez} – {gtitel}".rstrip(" –"), ""]
            continue
        if not enbez or enbez in ("Inhaltsübersicht", "Eingangsformel"):
            continue

        out.append(f"## {enbez} {ntitel}".rstrip())
        out.append("")
        if inhalt is not None:
            text = text_von(inhalt)
            out.append(text if text else "(weggefallen)")
        else:
            out.append("(weggefallen)")
        out.append("")

    return "\n".join(out).rstrip() + "\n", titel, abk


# Nur IPv4 verwenden: über IPv6 hängt die Verbindung auf manchen Servern.
_getaddrinfo = socket.getaddrinfo
socket.getaddrinfo = lambda host, *a, **k: [
    x for x in _getaddrinfo(host, *a, **k) if x[0] == socket.AF_INET]


def lade(slug, versuche=3):
    req = urllib.request.Request(URL.format(slug=slug), headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) gesetze-laden/1.0"})
    for versuch in range(1, versuche + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                daten = r.read()
            break
        except OSError:
            if versuch == versuche:
                raise
            time.sleep(5 * versuch)
    with zipfile.ZipFile(io.BytesIO(daten)) as z:
        name = next(n for n in z.namelist() if n.endswith(".xml"))
        return z.read(name)


def schreibe_index():
    zeilen = ["# Gesetzestexte (Strafrecht)", "",
              "Automatisch geladen von https://www.gesetze-im-internet.de "
              "(amtliche Werke, § 5 UrhG, gemeinfrei).", "",
              "| Datei | Gesetz | Abgerufen |", "|---|---|---|"]
    for datei in sorted(ZIEL.glob("*.md")):
        if datei.name == "README.md":
            continue
        erste = datei.read_text(encoding="utf-8").splitlines()
        titel = erste[0].lstrip("# ") if erste else datei.stem
        datum = next((z.split(": ", 1)[1] for z in erste if z.startswith("Abgerufen:")), "")
        zeilen.append(f"| [{datei.name}]({datei.name}) | {titel} | {datum} |")
    (ZIEL / "README.md").write_text("\n".join(zeilen) + "\n", encoding="utf-8")


def main(args):
    ZIEL.mkdir(exist_ok=True)
    if args[:1] == ["--xml"]:
        md, titel, _ = zu_markdown(Path(args[1]).read_bytes(), Path(args[1]).stem)
        sys.stdout.write(md)
        return 0

    fehler = 0
    for slug in args or list(GESETZE):
        try:
            md, titel, abk = zu_markdown(lade(slug), slug)
            (ZIEL / f"{slug}.md").write_text(md, encoding="utf-8")
            print(f"OK   {slug:12} {abk}: {md.count(chr(10) + '## ')} Vorschriften")
        except Exception as e:  # ein Gesetz darf fehlschlagen, der Rest läuft weiter
            fehler += 1
            print(f"FEHLER {slug}: {e}", file=sys.stderr)
    schreibe_index()
    return 1 if fehler == len(args or GESETZE) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
