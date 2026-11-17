"""Erstellt die Diagramme für die Dokumentation als PNG im Ordner diagramme/.

Aufruf: python3 diagramme.py
"""

import matplotlib

matplotlib.use("Agg")  # ohne Fenster zeichnen (keine GUI nötig)
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import analyse
import daten

ZIEL = daten.ORDNER / "diagramme"

# Farben: dunkles, ruhiges Schema. Die vier Reihenfarben sind auf Farbenblindheit geprüft
# (validate_palette.js, dunkler Modus: alle Prüfungen bestanden).
HINTERGRUND, FLAECHE = "#0d0d0d", "#1a1a19"
TEXT, TEXT2, GEDAEMPFT = "#f0efec", "#c3c2b7", "#898781"
RASTER, ACHSE = "#2c2c2a", "#383835"
FARBE = {"Wohnräume": "#3987e5", "Keller": "#d95926", "Schlafzimmer": "#199e70", "Küche-Sockel": "#c98500"}
WHO_FARBE, AT_FARBE = "#fab219", "#d03b3b"
# Ein Farbton von dunkel (wenig) nach hell (viel): wenig Radon verschwindet im Hintergrund.
BLAU_SKALA = matplotlib.colors.LinearSegmentedColormap.from_list("blau", ["#1a1a19", "#184f95", "#3987e5", "#cde2fb"])
PHASEN_GRAU = {"Frühling: morgens lüften": "#1f1f1e", "Sommer: Fenster offen": "#262624",
               "Urlaub: alles zu": "#33302a", "Lüftungsanlage": "#1f2630"}

plt.rcParams.update({
    "figure.facecolor": HINTERGRUND, "axes.facecolor": FLAECHE, "savefig.facecolor": HINTERGRUND,
    "text.color": TEXT, "axes.labelcolor": TEXT2, "xtick.color": GEDAEMPFT, "ytick.color": GEDAEMPFT,
    "axes.edgecolor": ACHSE, "axes.grid": True, "grid.color": RASTER, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.axisbelow": True, "axes.spines.right": False, "font.size": 11,
    "axes.titlesize": 13, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "legend.frameon": False, "lines.linewidth": 2, "font.family": "sans-serif",
})


def gruppen(H):
    """Fasst die 7 Sensoren zu 4 gut lesbaren Gruppen zusammen."""
    return pd.DataFrame({
        "Wohnräume": analyse.mittel(H, daten.WOHNRAEUME),
        "Keller": analyse.mittel(H, daten.KELLER),
        "Schlafzimmer": H["radon_Schlafzimmer"],
        "Küche-Sockel": H["radon_Kueche - Sockel"],
    })


def datumsachse(ax, format_="%d.%m."):
    ax.xaxis.set_major_formatter(mdates.DateFormatter(format_))


def grenzwerte(ax, x_text):
    """Zeichnet WHO- und Österreich-Wert als beschriftete Linien."""
    for wert, farbe, text in [(100, WHO_FARBE, "WHO-Empfehlung 100"), (300, AT_FARBE, "Referenzwert Österreich 300")]:
        ax.axhline(wert, color=farbe, lw=1.2, alpha=0.9, zorder=1)
        ax.text(x_text, wert + 6, text, color=farbe, fontsize=9, va="bottom")


def phasen_baender(ax, z, ende):
    """Hinterlegt die erkannten Phasen als graue Bänder mit Beschriftung oben."""
    teile = [("Frühling: morgens lüften", None, None)]
    if z["fenster_offen"]:
        teile.append(("Fenster offen", z["fenster_offen"]["von"], z["kwl"]["ab"] if z["kwl"] else z["fenster_offen"]["bis"]))
    if z["urlaub"]:
        teile.append(("Urlaub", z["urlaub"]["von"], z["urlaub"]["bis"]))
    if z["kwl"]:
        teile.append(("Lüftungsanlage", z["kwl"]["ab"], ende))
    for name, a, b in teile:
        if a is None:  # Frühling = Zeit vor allen anderen Phasen, nur beschriften
            ax.text(0.01, 0.98, name, transform=ax.transAxes, color=TEXT2, fontsize=9, va="top")
            continue
        ax.axvspan(pd.Timestamp(a), pd.Timestamp(b), color="#ffffff", alpha=0.05 if name != "Urlaub" else 0.10, lw=0, zorder=0)
        ax.text(pd.Timestamp(a) + pd.Timedelta("12h"), 0.98, name, transform=ax.get_xaxis_transform(),
                color=TEXT2, fontsize=9, va="top")


def legende(ax, **kw):
    ax.legend(loc=kw.pop("loc", "upper left"), ncol=kw.pop("ncol", 4), fontsize=10, labelcolor=TEXT2, **kw)


def speichern(fig, name):
    fig.savefig(ZIEL / name, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print("  gespeichert:", f"diagramme/{name}")


# ---------------------------------------------------------------------------

def d_ueberblick(H, z):
    """Gesamtverlauf: Tagesmittel der vier Gruppen über die ganze Messzeit."""
    G = gruppen(H).resample("1D").mean()
    fig, ax = plt.subplots(figsize=(14, 5.5))
    phasen_baender(ax, z, H.index[-1])
    for name in G:
        ax.plot(G.index, G[name], color=FARBE[name], label=name, lw=1.8)
    grenzwerte(ax, G.index[1])
    ax.set_ylim(0, 450)
    ax.set_ylabel("Radon in Bq/m³ (Tagesmittel)")
    ax.set_title("Radon im ganzen Haus, März bis Oktober 2026")
    datumsachse(ax)
    legende(ax, loc="upper right", bbox_to_anchor=(1, 0.93))
    speichern(fig, "01_ueberblick.png")


def d_heatmap(H, z):
    """Uhrzeit × Tag: zeigt Tagesrhythmus und Phasenwechsel auf einen Blick."""
    G = gruppen(H)
    fig, achsen = plt.subplots(2, 1, figsize=(14, 7), sharex=True)
    for ax, name in zip(achsen, ["Wohnräume", "Keller"]):
        s = G[name].to_frame("v")
        s["tag"], s["stunde"] = s.index.normalize(), s.index.hour
        M = s.pivot_table(index="stunde", columns="tag", values="v")
        bild = ax.pcolormesh(M.columns, M.index, M.clip(upper=200), cmap=BLAU_SKALA,
                             vmin=0, vmax=200, shading="auto")
        ax.set_title(f"{name}: Radon nach Uhrzeit und Tag")
        ax.set_ylabel("Uhrzeit")
        ax.set_yticks([0, 6, 12, 18, 23])
        ax.grid(False)
    leiste = fig.colorbar(bild, ax=achsen, shrink=0.8, pad=0.01)
    leiste.set_label("Bq/m³ (ab 200 gleich hell)", color=TEXT2)
    datumsachse(achsen[-1])
    speichern(fig, "02_heatmap_tag_uhrzeit.png")


def d_urlaub(T, z, e):
    """Urlaub als Experiment: Radon steigt, CO₂ fällt, beide mit angepasster Kurve."""
    u = z["urlaub"]
    a, b = pd.Timestamp(u["von"]) - pd.Timedelta("1D"), pd.Timestamp(u["bis"]) + pd.Timedelta("1D")
    X = T[a:b]
    G = gruppen(X)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8), sharex=True)
    for ax in (ax1, ax2):
        ax.axvspan(pd.Timestamp(u["von"]), pd.Timestamp(u["bis"]), color="#ffffff", alpha=0.06, lw=0)
    for name in G:
        ax1.plot(G.index, G[name].rolling(6, center=True, min_periods=2).mean(), color=FARBE[name], label=name, lw=1.5)
    grenzwerte(ax1, X.index[5])
    gl = e["urlaub_physik"]["radon"]["Kueche"]["gleichgewicht"]
    ax1.axhline(gl, color=TEXT2, lw=1)
    ax1.text(X.index[5], gl + 8, f"berechnetes Gleichgewicht ≈ {gl:.0f}", color=TEXT2, fontsize=9)
    ax1.set_ylabel("Radon in Bq/m³")
    ax1.set_title(f"Urlaub {pd.Timestamp(u['von']):%d.%m.} – {pd.Timestamp(u['bis']):%d.%m.}: niemand da, alles zu")
    legende(ax1, loc="upper left", bbox_to_anchor=(0, 0.99))
    for raum, farbe in [("Kueche", FARBE["Wohnräume"]), ("Schlafzimmer", FARBE["Schlafzimmer"])]:
        ax2.plot(X.index, X[f"co2_{raum}"], color=farbe, label=f"CO₂ {raum.replace('ue', 'ü')}", lw=1.5)
    ax2.axhline(420, color=GEDAEMPFT, lw=1)
    ax2.text(X.index[5], 425, "Außenluft ≈ 420 ppm", color=GEDAEMPFT, fontsize=9, va="bottom")
    n = e["urlaub_physik"]["co2"]
    ax2.set_title(f"CO₂ sinkt nur langsam → Luftwechsel nur {n['Schlafzimmer']['luftwechsel_pro_h']*100:.0f}–{n['Kueche']['luftwechsel_pro_h']*100:.0f} % pro Stunde")
    ax2.set_ylabel("CO₂ in ppm")
    legende(ax2, loc="upper right", ncol=2)
    datumsachse(ax2)
    speichern(fig, "03_urlaub_experiment.png")


def d_tagesgang(e):
    """Kleine Vielfache: durchschnittlicher Tagesverlauf je Phase."""
    tg = e["tagesgang"]
    fig, achsen = plt.subplots(1, 4, figsize=(16, 4.5), sharey=True)
    for ax, phase in zip(achsen, analyse.PHASEN_REIHENFOLGE):
        for name, farbe in [("Wohnräume", FARBE["Wohnräume"]), ("Keller", FARBE["Keller"]), ("Schlafzimmer", FARBE["Schlafzimmer"])]:
            werte = [np.nan if v is None else v for v in tg[phase][name]]
            ax.plot(range(24), werte, color=farbe, label=name)
        ax.set_title(phase, fontsize=11)
        ax.set_xticks([0, 6, 12, 18])
        ax.set_xlabel("Uhrzeit")
    achsen[0].set_ylabel("Radon in Bq/m³ (Mittel)")
    achsen[0].set_yscale("log")
    achsen[0].set_yticks([10, 20, 50, 100, 200, 400])
    achsen[0].get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    legende(achsen[0], ncol=1, loc="lower left")
    fig.suptitle("Tagesverlauf je Phase (logarithmische Achse)", x=0.01, ha="left", fontweight="bold")
    speichern(fig, "04_tagesgang_phasen.png")


def d_kamineffekt(e):
    """Radon gegen Temperaturunterschied innen − außen, vor und mit Lüftungsanlage."""
    w = e["wetter"]
    fig, achsen = plt.subplots(1, 2, figsize=(13, 4.8), sharey=True)
    for ax, teil in zip(achsen, ["vor Lüftungsanlage", "mit Lüftungsanlage"]):
        d = w[teil]["dT"]
        x = np.arange(len(d["klassen"]))
        for name, schluessel, versatz in [("Wohnräume", "wohn", -0.18), ("Keller", "keller", 0.18)]:
            werte = [np.nan if v is None else v for v in d[schluessel]]
            ax.bar(x + versatz, werte, width=0.34, color=FARBE[name], label=name)
        ax.set_xticks(x, [k.replace(" bis ", " … ") for k in d["klassen"]], fontsize=9)
        ax.set_xlabel("Innen minus außen in °C   (rechts = draußen kälter)")
        ax.set_title(teil)
        ax.grid(axis="x", visible=False)
    achsen[0].set_ylabel("Radon in Bq/m³ (Mittel)")
    legende(achsen[0], ncol=1)
    fig.suptitle("Kamineffekt: Je kälter es draußen ist, desto mehr Radon in den Wohnräumen",
                 x=0.01, ha="left", fontweight="bold")
    speichern(fig, "05_kamineffekt.png")


def d_fairer_vergleich(e):
    """Nächte mit geschlossenem Fenster: ohne vs. mit Lüftungsanlage, nach Außentemperatur."""
    f = e["fairer_vergleich"]
    tab = pd.DataFrame(f["tabelle"])
    klassen = list(dict.fromkeys(tab["aussen"]))
    x = np.arange(len(klassen))
    fig, ax = plt.subplots(figsize=(10, 4.8))
    for gruppe, farbe, versatz in [("ohne Anlage", FARBE["Keller"], -0.18), ("mit Anlage", FARBE["Wohnräume"], 0.18)]:
        t = tab[tab.gruppe == gruppe].set_index("aussen").reindex(klassen)
        balken = ax.bar(x + versatz, t["radon_wohn"], width=0.34, color=farbe, label=gruppe)
        for b, n in zip(balken, t["naechte"]):
            if not np.isnan(n):
                ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.5, f"{int(n)} N.", ha="center", fontsize=8, color=GEDAEMPFT)
    ax.set_xticks(x, [f"außen {k}" for k in klassen])
    ax.set_ylabel("Radon Wohnräume nachts (Bq/m³)")
    ax.set_title(f"Fairer Vergleich: Fenster zu, gleiche Temperatur → im Schnitt {f['senkung_proz']:.0f} % weniger mit Anlage")
    ax.grid(axis="x", visible=False)
    legende(ax, ncol=2, loc="upper right")
    speichern(fig, "06_fairer_vergleich.png")


def d_lueften(e):
    """Mittlere Wirkung des Morgenlüftens und Uhrzeit aller Lüftungsereignisse."""
    lw, ev = e["lueften_wirkung"], e["lueftungsereignisse"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 4.6), gridspec_kw={"width_ratios": [1.3, 1]})
    ax1.plot(lw["kurve_stunden"], lw["kurve_prozent"], color=FARBE["Wohnräume"])
    ax1.axvline(0, color=GEDAEMPFT, lw=1)
    ax1.text(0.2, 98, "Fenster auf", color=GEDAEMPFT, fontsize=9, va="top")
    ax1.set_xlabel("Stunden nach dem Lüften")
    ax1.set_ylabel("Radon in % vom Wert davor")
    ax1.set_title(f"Morgenlüften wirkt sofort ({lw['anzahl']} Ereignisse gemittelt)")
    stunden = pd.Series([pd.Timestamp(x["zeit"]).hour for x in ev]).value_counts().reindex(range(24), fill_value=0)
    ax2.bar(stunden.index, stunden.values, color=FARBE["Wohnräume"], width=0.8)
    ax2.set_xticks([0, 6, 12, 18, 23])
    ax2.set_xlabel("Uhrzeit")
    ax2.set_ylabel("Anzahl")
    ax2.set_title(f"Wann wurde gelüftet? ({len(ev)} erkannte Ereignisse)")
    ax2.grid(axis="x", visible=False)
    speichern(fig, "07_lueften.png")


def d_korrelation(e):
    """Wie ähnlich verlaufen die Räume? (−1 gegenläufig … +1 gleich)"""
    m = pd.DataFrame(e["korrelationen"]["matrix"]).loc[daten.RAEUME, daten.RAEUME]
    fig, ax = plt.subplots(figsize=(7.5, 6.2))
    bild = ax.imshow(m.values, cmap="RdBu_r", vmin=-1, vmax=1)
    namen = [r.replace("Kueche", "Küche").replace("Buero", "Büro") for r in daten.RAEUME]
    ax.set_xticks(range(len(namen)), namen, rotation=40, ha="right")
    ax.set_yticks(range(len(namen)), namen)
    for i in range(len(namen)):
        for j in range(len(namen)):
            ax.text(j, i, f"{m.values[i, j]:.2f}", ha="center", va="center", fontsize=8,
                    color=TEXT if abs(m.values[i, j]) > 0.5 else "#0b0b0b")
    ax.grid(False)
    fig.colorbar(bild, ax=ax, shrink=0.8).set_label("Korrelation", color=TEXT2)
    ax.set_title("Welche Räume hängen zusammen?\n(Stundenwerte, ohne Urlaub)")
    speichern(fig, "08_korrelation_raeume.png")


def d_kwl_wechsel(T, z):
    """Zoom auf den Start der Lüftungsanlage: Keller fällt und verläuft danach wie die Wohnräume."""
    ab = pd.Timestamp(z["kwl"]["ab"])
    X = gruppen(T[ab - pd.Timedelta("10D"):ab + pd.Timedelta("12D")]).rolling(6, center=True, min_periods=2).mean()
    fig, ax = plt.subplots(figsize=(13, 4.8))
    ax.axvspan(ab, X.index[-1], color="#ffffff", alpha=0.05, lw=0)
    ax.text(ab + pd.Timedelta("6h"), 0.97, "Lüftungsanlage", transform=ax.get_xaxis_transform(), color=TEXT2, fontsize=9, va="top")
    for name in ["Wohnräume", "Keller", "Küche-Sockel"]:
        ax.plot(X.index, X[name], color=FARBE[name], label=name, lw=1.5)
    grenzwerte(ax, X.index[3])
    ax.set_ylim(0, 320)
    ax.set_ylabel("Radon in Bq/m³")
    ax.set_title("Start der Lüftungsanlage: Der Keller sinkt von über 200 auf das Niveau der Wohnräume")
    datumsachse(ax)
    legende(ax, ncol=3, loc="upper right", bbox_to_anchor=(1, 0.86))
    speichern(fig, "09_start_lueftungsanlage.png")


def d_anlauf(df):
    """Datenqualität: Was ein Sensor-Neustart in den Rohdaten anrichtet."""
    spalte, betrieb = "Kueche – Radon (Bq/m³)", "Kueche – Betriebszeit (min)"
    roh = df.loc[df[spalte].notna(), ["zeit", spalte, betrieb]].set_index("zeit")
    fenster = roh["2026-04-16 04:00":"2026-04-16 11:00"]
    fig, ax = plt.subplots(figsize=(11, 4))
    anlauf = fenster[betrieb] < daten.ANLAUFZEIT_MIN
    ax.plot(fenster.index, fenster[spalte], color=FARBE["Wohnräume"], lw=1.5, marker="o", ms=4, label="Rohwerte")
    ax.scatter(fenster.index[anlauf], fenster[spalte][anlauf], s=60, color=AT_FARBE, zorder=3, label="erste Stunde nach Neustart (entfernt)")
    ax.set_ylabel("Radon in Bq/m³")
    ax.set_title("Neustart am 16.04.: Der Sensor meldet zuerst 0 und braucht ca. 1 Stunde")
    datumsachse(ax, "%H:%M")
    legende(ax, ncol=2, loc="upper left")
    ax.set_ylim(-5, 110)
    speichern(fig, "10_neustart_anlauf.png")


def main():
    ZIEL.mkdir(exist_ok=True)
    try:
        df = daten.lade_rohdaten()
    except daten.DatenFehler as fehler:
        print(f"Fehler: {fehler}")
        raise SystemExit(1)
    serien, _ = daten.bereinige(df)
    T, H = daten.raster(serien, "10min"), daten.raster(serien, "1h")
    e = analyse.analysiere()
    z = e["zeitraeume"]
    print("Erstelle Diagramme …")
    d_ueberblick(H, z)
    d_heatmap(H, z)
    if z["urlaub"]:
        d_urlaub(T, z, e)
    d_tagesgang(e)
    d_kamineffekt(e)
    if e["fairer_vergleich"]:
        d_fairer_vergleich(e)
    d_lueften(e)
    d_korrelation(e)
    if z["kwl"]:
        d_kwl_wechsel(T, z)
    d_anlauf(df)


if __name__ == "__main__":
    main()
