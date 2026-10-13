
from pathlib import Path
import pandas as pd

# 1. Chargement des données extraites

projet = Path(__file__).resolve().parent.parent

fichier = projet / "03_DONNEES_TRAITEES" / "abattages_volailles.csv"

df = pd.read_csv(fichier, parse_dates=["Date"])

print("Nombre de lignes :", len(df))

# 2. Contrôle des valeurs manquantes

print("\nVALEURS MANQUANTES")
print(df.isnull().sum())

# 3. Contrôle des doublons

doublons = df.duplicated(subset=["Date"]).sum()

print("\nNombre de dates en double :", doublons)

# 4. Contrôle des volumes

volumes_invalides = (
    df["Volume_millions_tetes"] <= 0
).sum()

print("Volumes invalides :", volumes_invalides)

# 5. Vérification de la cohérence des dates

dates_incoherentes = (
    (df["Date"].dt.year != df["Annee"]) |
    (df["Date"].dt.month != df["Mois"])
).sum()

print("Dates incohérentes :", dates_incoherentes)

# 6. Validation finale

if (
    len(df) == 19
    and df.isnull().sum().sum() == 0
    and doublons == 0
    and volumes_invalides == 0
    and dates_incoherentes == 0
):
    print("\nCONTROLES QUALITE : OK")
else:
    print("\nCONTROLES QUALITE : ANOMALIES")