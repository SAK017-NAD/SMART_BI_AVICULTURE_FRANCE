
from pathlib import Path
import pandas as pd

# 1. Chargement des données
projet = Path(__file__).resolve().parent.parent

fichier = (
    projet / "03_DONNEES_TRAITEES"
    / "abattages_volailles.csv"
)

df = pd.read_csv(fichier, parse_dates=["Date"])

# 2. Sélection des mois à comparer
juillet_2025 = df.loc[
    df["Date"] == "2025-07-01",
    "Volume_millions_tetes"
].iloc[0]

juillet_2026 = df.loc[
    df["Date"] == "2026-07-01",
    "Volume_millions_tetes"
].iloc[0]

# 3. Calcul de l'évolution annuelle
evolution = (
    (juillet_2026 - juillet_2025)
    / juillet_2025
) * 100

print("Juillet 2025 :", round(juillet_2025, 2))
print("Juillet 2026 :", round(juillet_2026, 2))

print("Evolution annuelle :", round(evolution, 1), "%")

# 4. Comparaison avec le PDF Agreste
volume_officiel = 73.0
evolution_officielle = -1.6

test_volume = (
    round(juillet_2026, 1) == volume_officiel
)

test_evolution = (
    round(evolution, 1) == evolution_officielle
)

print("\nVALIDATION OFFICIELLE")
print("Volume :", "OK" if test_volume else "KO")
print("Evolution :", "OK" if test_evolution else "KO")

if test_volume and test_evolution:
    print("\nRECETTE : VALIDEE")
else:
    print("\nRECETTE : ANOMALIE A ANALYSER")