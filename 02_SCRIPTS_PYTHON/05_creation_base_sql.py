
from pathlib import Path
import sqlite3
import pandas as pd

# 1. Chemins du projet
projet = Path(__file__).resolve().parent.parent
dossier = projet / "03_DONNEES_TRAITEES"
sortie = projet / "04_SQL"
sortie.mkdir(exist_ok=True)

# 2. Lecture des deux fichiers CSV
mensuels = pd.read_csv(
    dossier / "abattages_volailles.csv"
)

especes = pd.read_csv(
    dossier / "abattages_par_espece_juillet2026.csv"
)

# 3. Contrôles préalables
assert len(mensuels) == 19, "Nombre de mois incorrect"
assert len(especes) == 8, "Nombre d'espèces incorrect"

assert not mensuels["Date"].duplicated().any()
assert not especes[["Date", "Espece"]].duplicated().any()

assert mensuels["Volume_millions_tetes"].notna().all()
assert especes["Volume_millions_tetes"].notna().all()

assert (mensuels["Volume_millions_tetes"] >= 0).all()
assert (especes["Volume_millions_tetes"] >= 0).all()

# Vérifier que le détail correspond au total de juillet 2026
total_juillet = mensuels.loc[
    mensuels["Date"] == "2026-07-01",
    "Volume_millions_tetes"
].iloc[0]

total_especes = especes["Volume_millions_tetes"].sum()

assert abs(total_juillet - total_especes) < 0.0001, (
    "Le total par espèce ne correspond pas au total mensuel"
)

# 4. Construction de la dimension Date
dates = mensuels[["Date", "Annee", "Mois"]].copy()
dates = dates.rename(columns={
    "Date": "date_id",
    "Annee": "annee",
    "Mois": "mois"
})

# 5. Construction de la dimension Espèce
dim_espece = especes[["Espece"]].drop_duplicates().copy()
dim_espece = dim_espece.sort_values("Espece")
dim_espece = dim_espece.reset_index(drop=True)

dim_espece.insert(
    0, "espece_id",
    range(1, len(dim_espece) + 1)
)

dim_espece = dim_espece.rename(
    columns={"Espece": "nom_espece"}
)

# 6. Construction des tables de faits
fait_mensuel = mensuels[[
    "Date", "Volume_millions_tetes"
]].rename(columns={
    "Date": "date_id",
    "Volume_millions_tetes": "volume_millions_tetes"
})

fait_especes = especes.merge(
    dim_espece,
    left_on="Espece",
    right_on="nom_espece",
    validate="many_to_one"
)

fait_especes = fait_especes.rename(columns={
    "Date": "date_id",
    "Volume_millions_tetes": "volume_millions_tetes",
    "Evolution_annuelle_pct": "evolution_annuelle_pct",
    "Evolution_moyenne_pct": "evolution_moyenne_pct"
})

fait_especes = fait_especes[[
    "date_id",
    "espece_id",
    "volume_millions_tetes",
    "evolution_annuelle_pct",
    "evolution_moyenne_pct"
]]

# 7. Création de la base SQLite
chemin_base = sortie / "smart_bi_volaille.db"

with sqlite3.connect(chemin_base) as connexion:
    connexion.execute("PRAGMA foreign_keys = ON")

    # Supprimer les anciennes tables pour pouvoir
    # réexécuter le script sans créer de doublons.
    for table in [
        "FAIT_ABATTAGES_ESPECES",
        "FAIT_ABATTAGES_MENSUELS",
        "DIM_ESPECE",
        "DIM_DATE"
    ]:
        connexion.execute(f"DROP TABLE IF EXISTS {table}")

    connexion.executescript("""
        CREATE TABLE DIM_DATE (
            date_id TEXT PRIMARY KEY,
            annee INTEGER NOT NULL,
            mois INTEGER NOT NULL
        );

        CREATE TABLE DIM_ESPECE (
            espece_id INTEGER PRIMARY KEY,
            nom_espece TEXT NOT NULL UNIQUE
        );

        CREATE TABLE FAIT_ABATTAGES_MENSUELS (
            date_id TEXT PRIMARY KEY,
            volume_millions_tetes REAL NOT NULL,
            FOREIGN KEY (date_id)
                REFERENCES DIM_DATE(date_id)
        );

        CREATE TABLE FAIT_ABATTAGES_ESPECES (
            date_id TEXT NOT NULL,
            espece_id INTEGER NOT NULL,
            volume_millions_tetes REAL NOT NULL,
            evolution_annuelle_pct REAL,
            evolution_moyenne_pct REAL,
            PRIMARY KEY (date_id, espece_id),
            FOREIGN KEY (date_id)
                REFERENCES DIM_DATE(date_id),
            FOREIGN KEY (espece_id)
                REFERENCES DIM_ESPECE(espece_id)
        );
    """)

    # Importer les dimensions avant les faits
    dates.to_sql(
        "DIM_DATE", connexion,
        if_exists="append", index=False
    )

    dim_espece.to_sql(
        "DIM_ESPECE", connexion,
        if_exists="append", index=False
    )

    fait_mensuel.to_sql(
        "FAIT_ABATTAGES_MENSUELS", connexion,
        if_exists="append", index=False
    )

    fait_especes.to_sql(
        "FAIT_ABATTAGES_ESPECES", connexion,
        if_exists="append", index=False
    )

    # 8. Contrôles SQL
    print("\nVERIFICATION DES TABLES")

    for table in [
        "DIM_DATE",
        "DIM_ESPECE",
        "FAIT_ABATTAGES_MENSUELS",
        "FAIT_ABATTAGES_ESPECES"
    ]:
        nombre = connexion.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        print(f"{table} : {nombre} lignes")

    # Vérifier les clés étrangères
    erreurs = connexion.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    assert not erreurs, f"Erreurs de relations : {erreurs}"

print("\nBASE SQL CREEE AVEC SUCCES")
print("Emplacement :", chemin_base)