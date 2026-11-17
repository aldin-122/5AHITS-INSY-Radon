"""Tests für daten.py und analyse.py (Standardbibliothek unittest, nichts zu installieren).

Aufruf: python3 -m unittest -v test_analyse
"""

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

import analyse
import daten
import radon_laender
import webseite


class FehlerfaelleTest(unittest.TestCase):
    """Kaputte oder fehlende Eingaben müssen eine verständliche Meldung liefern."""

    def setUp(self):
        self.ordner = Path(tempfile.mkdtemp())

    def datei(self, inhalt, name="test.csv", modus="w"):
        pfad = self.ordner / name
        if modus == "wb":
            pfad.write_bytes(inhalt)
        else:
            pfad.write_text(inhalt, encoding="utf-8")
        return pfad

    def test_datei_fehlt(self):
        with self.assertRaisesRegex(daten.DatenFehler, "nicht gefunden"):
            daten.lade_rohdaten(self.ordner / "gibtsnicht.csv")

    def test_datei_leer(self):
        with self.assertRaisesRegex(daten.DatenFehler, "leer"):
            daten.lade_rohdaten(self.datei(""))

    def test_falsche_spalten(self):
        with self.assertRaisesRegex(daten.DatenFehler, "fehlen Spalten"):
            daten.lade_rohdaten(self.datei("a,b\n1,2\n"))

    def test_nur_kopfzeile(self):
        kopf = ",".join(daten.PFLICHTSPALTEN) + "\n"
        with self.assertRaisesRegex(daten.DatenFehler, "keine Messwerte"):
            daten.lade_rohdaten(self.datei(kopf))

    def test_binaerdatei(self):
        with self.assertRaises(daten.DatenFehler):
            daten.lade_rohdaten(self.datei(bytes(range(256)) * 50, "kaputt.csv", "wb"))

    def test_kaputte_zeitstempel_und_werte(self):
        kopf = ",".join(daten.PFLICHTSPALTEN)
        leer = "," * (len(daten.PFLICHTSPALTEN) - 1)
        inhalt = f"{kopf}\nkeinDatum{leer}\n2026-04-01 10:00:00,abc{leer[1:]}\n"
        df = daten.lade_rohdaten(self.datei(inhalt))
        self.assertEqual(df.attrs["ungueltige_zeiten"], 1)
        self.assertEqual(len(df), 1)
        self.assertTrue(df[daten.PFLICHTSPALTEN[1]].isna().all())  # „abc“ → fehlt

    def test_analyse_ohne_co2(self):
        """Eine gültige Datei ohne Raumklima-Spalten kann nicht ausgewertet werden."""
        kopf = ",".join(daten.PFLICHTSPALTEN)
        werte = ",".join(["2026-04-01 10:00:00"] + ["20"] * (len(daten.PFLICHTSPALTEN) - 1))
        with self.assertRaisesRegex(daten.DatenFehler, "fehlen Messreihen"):
            analyse.analysiere(self.datei(f"{kopf}\n{werte}\n"))


class BereinigungTest(unittest.TestCase):
    """Prüft die Regeln für Anlaufwerte, CO₂-Fehler und doppelte Meldungen."""

    def test_anlauf_und_co2(self):
        df = pd.DataFrame({
            "zeit": pd.to_datetime(["2026-04-01 10:00", "2026-04-01 10:10", "2026-04-01 11:30", "2026-04-01 11:30"]),
            "Kueche – Radon (Bq/m³)": [0, 40, 55, 55],
            "Kueche – Betriebszeit (min)": [5, 15, 95, 95],
            "Kueche (Luft) – CO₂ (ppm)": [313, 500, None, None],
        })
        serien, bericht = daten.bereinige(df)
        self.assertEqual(list(serien["radon_Kueche"]), [55])          # Anlauf + doppelt entfernt
        self.assertEqual(bericht["anlauf"]["Kueche"], 2)
        self.assertEqual(list(serien["co2_Kueche"]), [500])           # 313 ppm unmöglich
        self.assertEqual(bericht["co2_fehler"], 1)


class EchteDatenTest(unittest.TestCase):
    """Ende-zu-Ende mit der echten Datei: Ergebnisse müssen plausibel sein."""

    @classmethod
    def setUpClass(cls):
        cls.e = analyse.analysiere()

    def test_zeitraeume_erkannt(self):
        z = self.e["zeitraeume"]
        self.assertTrue(z["urlaub"]["von"].startswith("2026-07-31"))
        self.assertTrue(z["urlaub"]["bis"].startswith("2026-08-06"))
        self.assertEqual(z["kwl"]["ab"], "2026-08-23")
        self.assertTrue("2026-06-15" <= z["fenster_offen"]["von"] <= "2026-06-30")

    def test_physik_stimmt_ueberein(self):
        """Luftwechsel aus CO₂ und aus Radon müssen in derselben Größenordnung liegen."""
        u = self.e["urlaub_physik"]
        n_co2 = u["co2"]["Schlafzimmer"]["luftwechsel_pro_h"]
        n_rn = u["radon"]["Schlafzimmer"]["luftwechsel_pro_h"]
        self.assertLess(abs(n_co2 - n_rn), 0.02)

    def test_kennzahlen_von_hand(self):
        """Mittelwert der Küche stichprobenartig direkt aus der CSV nachrechnen."""
        df = daten.lade_rohdaten()
        roh = df.loc[df["Kueche – Betriebszeit (min)"] >= daten.ANLAUFZEIT_MIN]
        s = roh.set_index("zeit")["Kueche – Radon (Bq/m³)"].dropna()
        s = s[~s.index.duplicated()].resample("1h").mean().dropna()
        self.assertAlmostEqual(s.mean(), self.e["kennzahlen"]["Kueche"]["gesamt"]["mittel"], delta=0.1)

    def test_lueftungsanlage_senkt(self):
        self.assertGreater(self.e["fairer_vergleich"]["senkung_proz"], 20)

    def test_dunstabzug_tag(self):
        """20.07.: ohne Kamineffekt (außen ≈ innen) strömt trotzdem mehr Radon nach als im Urlaub."""
        d = self.e["dunstabzug"]
        self.assertGreater(d["zustrom_bq_m3_h"], 1.5 * d["zustrom_urlaub"])
        self.assertGreater(d["temp_aussen_max"], d["temp_innen"] - 1)
        self.assertGreater(d["sockel_max"], d["wohn_max"])

    def test_fazit_zahlen(self):
        """Heizzeit mehr Radon als Sommer, Winter-Sog stärker als Sommer-Sog, Haus zu dicht."""
        f = self.e["fazit"]
        self.assertGreater(f["faktor_gemessen"], 2)
        self.assertGreater(f["druck"]["winter_pa"], 5 * f["druck"]["sommer_pa"])
        self.assertTrue(3 < f["druck"]["winter_pa"] < 6)          # Größenordnung laut Formel bei ≈ 5 m und 21 K
        self.assertGreater(f["dichtheit"]["faktor_zu_wenig"][0], 5)

    def test_gelueftet_von_anfang_an(self):
        """Laut Hausbesitzer wurde von Anfang an gelüftet: schon in der ersten Woche gibt es Lüftungsereignisse."""
        erste_woche = [x for x in self.e["lueftungsereignisse"] if x["zeit"] < "2026-03-31"]
        self.assertGreaterEqual(len(erste_woche), 5)


class WeltkugelTest(unittest.TestCase):
    """Ländergrenzen und Radonwerte für die Weltkugel."""

    def test_laender_mit_werten(self):
        w = webseite.welt_laender()
        self.assertGreater(len(w["laender"]), 150)
        at = next(l for l in w["laender"] if l["id"] == "040")
        self.assertEqual((at["n"], at["v"]), ("Österreich", 99))
        # jeder Ring hat eine gerade Anzahl Zahlen (Länge, Breite) und liegt im gültigen Bereich
        for land in w["laender"]:
            for r in land["r"]:
                self.assertEqual(len(r) % 2, 0)
                self.assertTrue(all(-180 <= x <= 180 for x in r[0::2]) and all(-90 <= y <= 90 for y in r[1::2]))
        self.assertEqual(sum(l["v"] is not None for l in w["laender"]), len(radon_laender.LAENDER))

    def test_kartendatei_fehlt(self):
        """Ohne Kartendatei gibt es keine Kugel, aber auch keinen Absturz."""
        self.assertIsNone(webseite.welt_laender(Path(tempfile.gettempdir()) / "gibt_es_nicht.json"))


class WebseiteTest(unittest.TestCase):
    """Die Website muss sich erzeugen lassen und darf keine fehlerhaften Daten enthalten."""

    def test_erzeugen(self):
        ziel = Path(tempfile.mkdtemp()) / "radon.html"
        webseite.erzeuge(ziel=ziel)
        inhalt = ziel.read_text(encoding="utf-8")
        self.assertNotIn(webseite.PLATZHALTER, inhalt)
        # Eingebettete Daten herausschneiden und streng prüfen: NaN/Infinity wären im Browser ungültig
        roh = inhalt.split("const DATEN = ", 1)[1].split(";\nconst FEHLER", 1)[0].replace("<\\/", "</")
        def verboten(wert):
            raise ValueError(f"ungültiger Wert im JSON: {wert}")
        daten_json = json.loads(roh, parse_constant=verboten)
        self.assertEqual(len(daten_json["auff"]), 31)
        self.assertGreater(len(inhalt), 100_000)

    def test_vorlage_fehlt(self):
        alt = webseite.VORLAGE
        webseite.VORLAGE = Path(tempfile.mkdtemp()) / "fehlt.html"
        try:
            with self.assertRaisesRegex(daten.DatenFehler, "Vorlage fehlt"):
                webseite.erzeuge(ziel=Path(tempfile.mkdtemp()) / "x.html")
        finally:
            webseite.VORLAGE = alt

    def test_alle_auffaelligkeiten_vollstaendig(self):
        import auffaelligkeiten
        liste = auffaelligkeiten.liste(analyse.analysiere())
        self.assertEqual(len({a["nr"] for a in liste}), len(liste))   # Nummern eindeutig
        for a in liste:
            for feld in ("titel", "von", "bis", "was", "warum"):
                self.assertTrue(a[feld], f"{a['nr']}: {feld} fehlt")
            self.assertLessEqual(a["von"], a["bis"], a["nr"])


if __name__ == "__main__":
    unittest.main()
