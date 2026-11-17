"""Radon in Wohnungen weltweit: Landesmittelwerte für die Weltkugel auf der Website.

Quelle: UNSCEAR 2006 Report, Vol. II, Annex E, Table 1 „Concentrations of radon in indoor air“
(arithmetisches Mittel in Bq/m³). Gibt es für ein Land mehrere Zeilen, wird die neuere
landesweite Erhebung genommen. Ausnahme Österreich: UNSCEAR nennt nur einen alten Wert
aus wenigen Messungen (15 Bq/m³); verwendet wird das Ergebnis der österreichischen
Radon-Erhebung ÖNRAP (Friedmann 2005, Health Physics): 99 Bq/m³.

Wichtig: Die Erhebungen stammen aus verschiedenen Jahren und wurden unterschiedlich
durchgeführt. Die Werte zeigen die Größenordnung, nicht eine genaue Rangliste.

Schlüssel = ISO-3166-Ländernummer (so heißen die Länder in der Kartendatei world-atlas).
"""

QUELLE = "UNSCEAR 2006, Annex E, Tabelle 1"
QUELLE_AT = "ÖNRAP (Friedmann 2005)"
WELTMITTEL = 46          # Bq/m³, UNSCEAR 2000 (ungewichtet); bevölkerungsgewichtet 39

# Nummer: (deutscher Name, arithmetisches Mittel in Bq/m³)
LAENDER = {
    # Afrika
    "012": ("Algerien", 30), "818": ("Ägypten", 9),
    # Nord- und Mittelamerika
    "124": ("Kanada", 28), "484": ("Mexiko", 140), "840": ("USA", 46), "192": ("Kuba", 8),
    # Südamerika
    "032": ("Argentinien", 35), "076": ("Brasilien", 82), "152": ("Chile", 25),
    "600": ("Paraguay", 28), "604": ("Peru", 32), "862": ("Venezuela", 53),
    # Asien
    "156": ("China", 44), "158": ("Taiwan", 10), "356": ("Indien", 57), "360": ("Indonesien", 35),
    "392": ("Japan", 16), "410": ("Südkorea", 53), "458": ("Malaysia", 14), "586": ("Pakistan", 30),
    "608": ("Philippinen", 23), "643": ("Russland", 55), "764": ("Thailand", 23),
    "051": ("Armenien", 104), "364": ("Iran", 82), "414": ("Kuwait", 14), "760": ("Syrien", 44),
    # Nordeuropa
    "208": ("Dänemark", 59), "233": ("Estland", 120), "246": ("Finnland", 120), "352": ("Island", 10),
    "440": ("Litauen", 49), "578": ("Norwegen", 73), "752": ("Schweden", 108),
    # Westeuropa
    "040": ("Österreich", 99), "056": ("Belgien", 48), "250": ("Frankreich", 89), "276": ("Deutschland", 50),
    "372": ("Irland", 89), "442": ("Luxemburg", 110), "528": ("Niederlande", 23), "756": ("Schweiz", 75),
    "826": ("Großbritannien", 20),
    # Osteuropa
    "100": ("Bulgarien", 22), "203": ("Tschechien", 118), "348": ("Ungarn", 107), "616": ("Polen", 49),
    "642": ("Rumänien", 25), "703": ("Slowakei", 87),
    # Südeuropa
    "008": ("Albanien", 120), "191": ("Kroatien", 35), "196": ("Zypern", 7), "300": ("Griechenland", 55),
    "380": ("Italien", 70), "499": ("Montenegro", 184), "620": ("Portugal", 62), "705": ("Slowenien", 87),
    "724": ("Spanien", 90),
    # Ozeanien
    "036": ("Australien", 11), "554": ("Neuseeland", 22),
}

# Hinweise, die im Tooltip zusätzlich erscheinen
HINWEISE = {
    "643": "UNSCEAR nennt 50–60",
    "040": "ÖNRAP; UNSCEAR nennt einen alten Wert (15)",
}
