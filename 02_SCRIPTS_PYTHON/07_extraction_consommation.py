
from pathlib import Path
import pandas as pd

# 1. Définir les chemins
projet = Path(__file__).resolve().parent.parent
source = projet / "01_DONNEES_BRUTES"
sortie = projet / "03_DONNEES_TRAITEES"

# 2. Rechercher notre fichier Agreste
fichiers = list(source.glob("*aviculture*.xlsx"))

if len(fichiers) != 1:
    raise ValueError("Fichier Agreste introuvable ou ambigu.")

# 3. Lire les données de consommation
df = pd.read_excel(
    fichiers[0],
    sheet_name="Fig 5b_ Graph Consommation",
    header=None
)

# 4. Transformer les données en format long
donnees = []

for annee, ligne in [(2025, 4), (2026, 5)]:
    for mois in range(1, 13):

        valeur = df.iat[ligne, mois + 1]

        if pd.notna(valeur):
            donnees.append({
                "Date": f"{annee}-{mois:02d}-01",
                "Annee": annee,
                "Mois": mois,
                "Consommation_milliers_tec": float(valeur)
            })

# 5. Construire la table
resultat = pd.DataFrame(donnees)

print("\nCONSOMMATION MENSUELLE")
print(resultat.to_string(index=False))

# 6. Contrôles qualité
assert len(resultat) == 18
assert not resultat["Date"].duplicated().any()
assert not resultat.isnull().any().any()
assert (resultat["Consommation_milliers_tec"] > 0).all()

# 7. Validation métier avec le PDF
juin_2025 = resultat.loc[
    resultat["Date"] == "2025-06-01",
    "Consommation_milliers_tec"
].iloc[0]

juin_2026 = resultat.loc[
    resultat["Date"] == "2026-06-01",
    "Consommation_milliers_tec"
].iloc[0]

evolution = (
    (juin_2026 - juin_2025)
    / juin_2025
) * 100

print("\nVALIDATION METIER")
print("Juin 2026 :", round(juin_2026, 1))
print("Evolution annuelle :", round(evolution, 1), "%")

assert round(juin_2026, 1) == 189.4
assert round(evolution, 1) == 3.9

print("CONTROLES ET VALIDATION : OK")

# 8. Export CSV
resultat.to_csv(
    sortie / "consommation_mensuelle.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nEXPORT CSV TERMINE")