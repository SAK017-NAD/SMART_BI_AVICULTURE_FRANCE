
from pathlib import Path
import pandas as pd

# 1. Chemins
projet = Path(__file__).resolve().parent.parent
source = projet / "01_DONNEES_BRUTES"
sortie = projet / "03_DONNEES_TRAITEES"

# Recherche du fichier Agreste
fichiers = list(source.glob("*aviculture*.xlsx"))

if len(fichiers) != 1:
    raise ValueError("Fichier Agreste introuvable ou ambigu.")

# 2. Lecture des données officielles
df = pd.read_excel(
    fichiers[0],
    sheet_name="Fig 1_ Tab Abatt volailles",
    header=None
)

# 3. Extraction des espèces
# Lignes Excel 8 à 15 et colonnes B à E
especes = df.iloc[7:15, [1, 2, 3, 4]].copy()

especes.columns = [
    "Espece",
    "Volume_millions_tetes",
    "Evolution_annuelle_pct",
    "Evolution_moyenne_pct"
]

# 4. Préparation
especes["Espece"] = (
    especes["Espece"].str.strip().str.rstrip("*")
)

especes.insert(0, "Date", "2026-07-01")

colonnes_numeriques = [
    "Volume_millions_tetes",
    "Evolution_annuelle_pct",
    "Evolution_moyenne_pct"
]

for colonne in colonnes_numeriques:
    especes[colonne] = pd.to_numeric(
        especes[colonne], errors="raise"
    )

# 5. Contrôle de cohérence avec le total officiel
total_officiel = float(df.iat[6, 2])
total_calcule = especes["Volume_millions_tetes"].sum()

if abs(total_calcule - total_officiel) > 0.000001:
    raise ValueError("Écart détecté avec le total officiel")

print(especes.to_string(index=False))
print("\nTotal calculé :", round(total_calcule, 2))
print("Total officiel :", round(total_officiel, 2))
print("CONTRÔLE : OK")

# 6. Export
especes.to_csv(
    sortie / "abattages_par_espece_juillet2026.csv",
    index=False,
    encoding="utf-8-sig"
)