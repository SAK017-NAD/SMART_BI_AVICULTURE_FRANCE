
from pathlib import Path
import pandas as pd

# 1. Définition des chemins
projet = Path(__file__).resolve().parent.parent
dossier_source = projet / "01_DONNEES_BRUTES"
dossier_sortie = projet / "03_DONNEES_TRAITEES"

dossier_sortie.mkdir(exist_ok=True)

# 2. Recherche du fichier Excel Agreste
fichiers = list(dossier_source.glob("*.xlsx"))

if len(fichiers) != 1:
    raise ValueError(
        "Le dossier doit contenir uniquement le fichier Excel Agreste."
    )

# 3. Lecture de l'onglet
df = pd.read_excel(
    fichiers[0],
    sheet_name="Fig 1_GRAPH abattages",
    header=None
)

# 4. Extraction et restructuration
donnees = []

for annee, ligne in [(2025, 3), (2026, 4)]:
    for mois in range(1, 13):

        valeur = df.iat[ligne, mois + 2]

        if pd.notna(valeur):
            donnees.append({
                "Date": f"{annee}-{mois:02d}-01",
                "Annee": annee,
                "Mois": mois,
                "Volume_millions_tetes": float(valeur)
            })

# 5. Création de notre table structurée
resultat = pd.DataFrame(donnees)

# 6. Export pour les prochaines étapes
resultat.to_csv(
    dossier_sortie / "abattages_volailles.csv",
    index=False,
    encoding="utf-8-sig"
)

print(resultat)
print("Nombre de lignes :", len(resultat))