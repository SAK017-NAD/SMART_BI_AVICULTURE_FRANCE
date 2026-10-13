
from pathlib import Path
import pandas as pd

# 1. Définition des chemins
projet = Path(__file__).resolve().parent.parent
source = projet / "01_DONNEES_BRUTES"
sortie = projet / "03_DONNEES_TRAITEES"

fichiers = list(source.glob("*aviculture*.xlsx"))

if len(fichiers) != 1:
    raise ValueError("Fichier Agreste introuvable ou ambigu.")

# 2. Lecture des prix
df = pd.read_excel(
    fichiers[0],
    sheet_name="Fig 3_IPPAP Vol",
    header=None
)

# Afficher les valeurs réellement lues
print("Années détectées :", repr(df.iat[4, 8]),
      repr(df.iat[4, 9]))

# Vérifier les années en acceptant
# les valeurs numériques ou textuelles
assert pd.to_numeric(df.iat[4, 8]) == 2025
assert pd.to_numeric(df.iat[4, 9]) == 2026

# 3. Extraction des données
donnees = []

for annee, colonne in [(2025, 8), (2026, 9)]:
    for mois in range(1, 13):

        ligne = mois + 4
        valeur = df.iat[ligne, colonne]

        if pd.notna(valeur):
            donnees.append({
                "Date": f"{annee}-{mois:02d}-01",
                "Annee": annee,
                "Mois": mois,
                "Indice_IPPAP": float(valeur)
            })

prix = pd.DataFrame(donnees)

# 4. Extraction de la moyenne historique
historique = []

for mois in range(1, 13):
    historique.append({
        "Mois": mois,
        "Moyenne_2021_2025": float(
            df.iat[mois + 4, 10]
        )
    })

reference = pd.DataFrame(historique)

# 5. Contrôles qualité
assert len(prix) == 19
assert len(reference) == 12
assert not prix["Date"].duplicated().any()
assert not prix.isnull().any().any()
assert (prix["Indice_IPPAP"] > 0).all()

# 6. Validation métier
def recuperer_indice(annee, mois):
    return prix.loc[
        (prix["Annee"] == annee)
        & (prix["Mois"] == mois),
        "Indice_IPPAP"
    ].iloc[0]

juin_2026 = recuperer_indice(2026, 6)
juillet_2025 = recuperer_indice(2025, 7)
juillet_2026 = recuperer_indice(2026, 7)

moyenne = reference.loc[
    reference["Mois"] == 7,
    "Moyenne_2021_2025"
].iloc[0]

evolution_mensuelle = (
    juillet_2026 / juin_2026 - 1
) * 100

evolution_annuelle = (
    juillet_2026 / juillet_2025 - 1
) * 100

evolution_historique = (
    juillet_2026 / moyenne - 1
) * 100

print("\nVALIDATION DES PRIX")
print("Indice juillet 2026 :", juillet_2026)
print("Evolution mensuelle :", round(evolution_mensuelle, 1), "%")
print("Evolution annuelle :", round(evolution_annuelle, 1), "%")
print("Ecart moyenne 5 ans :", round(evolution_historique, 1), "%")

assert round(evolution_mensuelle, 1) == 1.7
assert round(evolution_annuelle, 1) == 2.2
assert round(evolution_historique, 1) == 1.6

print("\nVALIDATION METIER : OK")

# 7. Exports
prix.to_csv(
    sortie / "prix_production_volailles.csv",
    index=False,
    encoding="utf-8-sig"
)

reference.to_csv(
    sortie / "prix_reference_historique.csv",
    index=False,
    encoding="utf-8-sig"
)

print("EXPORTS CSV TERMINES")