"""Erzeugt die Website radon.html (eine einzige Datei, ohne Server) und öffnet sie im Browser.

Aufruf: python3 webseite.py               → erzeugt und öffnet radon.html
        python3 webseite.py --kein-browser → nur erzeugen (z. B. für Tests)

Die Seite selbst (HTML/CSS/JavaScript) steht in webseite_vorlage.html. Dieses Skript
setzt dort nur die Daten als JSON ein. Alle Diagramme zeichnet JavaScript selbst,
deshalb braucht die Seite keine externen Bibliotheken und funktioniert auch offline.
"""

import json
import sys
import webbrowser

import analyse
import auffaelligkeiten
import daten
import radon_laender

VORLAGE = daten.ORDNER / "webseite_vorlage.html"
ZIEL = daten.ORDNER / "radon.html"
PLATZHALTER = "/*__DATEN__*/null"
# Ländergrenzen (world-atlas 2.0.2, Natural Earth 1:110 Mio., Lizenz in welt/LIZENZ_world-atlas.txt)
WELT_KARTE = daten.ORDNER / "welt" / "laender_110m.json"
ANTARKTIS = "010"   # weggelassen: liegt am Pol, verzerrt auf der Kugel stark und hat keine Wohnungen

# Diese Stundenreihen braucht die Seite (Radon aller Räume + Raumklima + Wetter).
REIHEN = [f"radon_{r}" for r in daten.RAEUME] + [
    "co2_Kueche", "co2_Schlafzimmer", "temp_Kueche", "temp_Schlafzimmer", "temp_Wetter",
    "feuchte_Kueche", "feuchte_Schlafzimmer", "druck_Kueche", "druck_Schlafzimmer", "druck_Wetter",
    "wind_Wetter",
]


def als_liste(serie, stellen=1):
    """Zeitreihe → Liste mit gerundeten Werten, fehlende Werte als None (wird in JSON zu null)."""
    return [None if v != v else round(float(v), stellen) for v in serie]


def welt_laender(karte=WELT_KARTE):
    """Liest die Ländergrenzen (TopoJSON) und hängt jedem Land seinen Radon-Mittelwert an.

    TopoJSON speichert jede Grenzlinie („arc“) nur einmal, als ganze Zahlen mit
    Differenzen zum Vorgänger. Hier werden daraus wieder Längen-/Breitengrade gemacht.
    Fehlt die Datei, gibt es keine Weltkugel, der Rest der Seite funktioniert trotzdem.
    """
    if not karte.exists():
        return None
    topo = json.loads(karte.read_text(encoding="utf-8"))
    (sx, sy), (tx, ty) = topo["transform"]["scale"], topo["transform"]["translate"]
    boegen = []
    for bogen in topo["arcs"]:
        x = y = 0
        punkte = []
        for dx, dy in bogen:
            x, y = x + dx, y + dy
            punkte.append((round(x * sx + tx, 1), round(y * sy + ty, 1)))
        boegen.append(punkte)

    def ring(indizes):
        """Setzt einen Ring aus Bögen zusammen (negativer Index = Bogen rückwärts)."""
        punkte = []
        for i in indizes:
            b = boegen[i] if i >= 0 else boegen[~i][::-1]
            punkte.extend(b if not punkte else b[1:])
        flach = []
        for p in punkte:   # nach dem Runden doppelte Nachbarpunkte weglassen (kleinere Datei)
            if flach[-2:] != list(p):
                flach.extend(p)
        return flach

    laender = []
    for g in topo["objects"]["countries"]["geometries"]:
        nr = g.get("id")
        if nr == ANTARKTIS or g.get("type") not in ("Polygon", "MultiPolygon"):
            continue
        polygone = [g["arcs"]] if g["type"] == "Polygon" else g["arcs"]
        name, wert = radon_laender.LAENDER.get(nr, (g["properties"]["name"], None))
        laender.append({"id": nr, "n": name, "v": wert, "h": radon_laender.HINWEISE.get(nr, ""),
                        "r": [ring(r) for poly in polygone for r in poly]})
    return {"laender": laender, "quelle": radon_laender.QUELLE, "quelle_at": radon_laender.QUELLE_AT,
            "weltmittel": radon_laender.WELTMITTEL}


def baue_daten(pfad=daten.CSV_STANDARD):
    """Sammelt alles, was die Website braucht, in einem dict."""
    df = daten.lade_rohdaten(pfad)
    serien, _ = daten.bereinige(df)
    H = daten.raster(serien, "1h")
    e = analyse.analysiere(pfad)

    # Rohwerte der Küche rund um einen Neustart (inkl. der entfernten Anlauf-Nullen) für C1
    roh = df.loc[df["Kueche – Radon (Bq/m³)"].notna(), ["zeit", "Kueche – Radon (Bq/m³)"]]
    roh = roh[(roh.zeit >= "2026-04-16 03:00") & (roh.zeit <= "2026-04-16 12:00")]

    return {
        "start": H.index[0].strftime("%Y-%m-%dT%H:%M"),
        "reihen": {name: als_liste(H[name], 2 if name.startswith("druck") else 1) for name in REIHEN if name in H},
        "roh": {"roh_Kueche": {"t": [t.strftime("%Y-%m-%dT%H:%M:%S") for t in roh.zeit],
                               "v": [float(v) for v in roh["Kueche – Radon (Bq/m³)"]]}},
        "e": e,
        "auff": auffaelligkeiten.liste(e),
        "welt": welt_laender(),
    }


def erzeuge(pfad=daten.CSV_STANDARD, ziel=ZIEL):
    """Setzt die Daten in die Vorlage ein und schreibt die fertige HTML-Datei."""
    if not VORLAGE.exists():
        raise daten.DatenFehler(f"Vorlage fehlt: {VORLAGE.name}")
    vorlage = VORLAGE.read_text(encoding="utf-8")
    if PLATZHALTER not in vorlage:
        raise daten.DatenFehler("In der Vorlage fehlt der Platzhalter für die Daten.")
    inhalt = json.dumps(baue_daten(pfad), ensure_ascii=False, separators=(",", ":"), default=str)
    # „</“ im JSON würde das <script>-Tag vorzeitig beenden → maskieren
    inhalt = inhalt.replace("</", "<\\/")
    ziel.write_text(vorlage.replace(PLATZHALTER, inhalt), encoding="utf-8")
    return ziel


def main():
    try:
        ziel = erzeuge()
    except daten.DatenFehler as fehler:
        print(f"Fehler: {fehler}")
        sys.exit(1)
    groesse = ziel.stat().st_size / 1024
    print(f"Website erzeugt: {ziel.name} ({groesse:.0f} KB)")
    if "--kein-browser" not in sys.argv:
        webbrowser.open(ziel.as_uri())


if __name__ == "__main__":
    main()
