
from pathlib import Path
import sqlite3
import pandas as pd

# 1. Chemins du projet
projet = Path(__file__).resolve().parent.parent
dossier = projet / "03_DONNEES_TRAITEES"
base = projet / "04_SQL" / "smart_bi_volaille.db"

if not base.exists():
    raise FileNotFoundError("Base SQL introuvable.")

# 2. Chargement des fichiers
consommation = pd.read_csv(
    dossier / "consommation_mensuelle.csv"
)

prix = pd.read_csv(
    dossier / "prix_production_volailles.csv"
)

historique = pd.read_csv(
    dossier / "prix_reference_historique.csv"
)

# 3. Contrôles avant intégration
assert len(consommation) == 18
assert len(prix) == 19
assert len(historique) == 12

assert consommation["Date"].is_unique
assert prix["Date"].is_unique
assert historique["Mois"].is_unique

assert consommation.notna().all().all()
assert prix.notna().all().all()
assert historique.notna().all().all()

assert (
    consommation["Consommation_milliers_tec"] > 0
).all()

assert (prix["Indice_IPPAP"] > 0).all()

# 4. Préparation des tables
fait_consommation = consommation[[
    "Date",
    "Consommation_milliers_tec"
]].rename(columns={
    "Date": "date_id",
    "Consommation_milliers_tec":
        "consommation_milliers_tec"
})

fait_prix = prix[[
    "Date",
    "Indice_IPPAP"
]].rename(columns={
    "Date": "date_id",
    "Indice_IPPAP": "indice_ippap"
})

ref_historique = historique.rename(columns={
    "Mois": "mois",
    "Moyenne_2021_2025": "indice_moyen"
})

# 5. Connexion à la base SQL
with sqlite3.connect(base) as conn:

    conn.execute("PRAGMA foreign_keys = ON")

    # Vérification des dates existantes
    dates = pd.read_sql_query(
        "SELECT date_id FROM DIM_DATE", conn
    )

    dates_existantes = set(dates["date_id"])

    dates_sources = (
        set(fait_consommation["date_id"])
        | set(fait_prix["date_id"])
    )

    assert dates_sources.issubset(dates_existantes), (
        "Certaines dates sont absentes de DIM_DATE"
    )

    # 6. Création des nouvelles tables
    conn.executescript("""
        DROP TABLE IF EXISTS FAIT_CONSOMMATION;
        DROP TABLE IF EXISTS FAIT_INDICE_PRIX;
        DROP TABLE IF EXISTS REF_PRIX_HISTORIQUE;

        CREATE TABLE FAIT_CONSOMMATION (
            date_id TEXT PRIMARY KEY,
            consommation_milliers_tec REAL NOT NULL,
            FOREIGN KEY (date_id)
                REFERENCES DIM_DATE(date_id)
        );

        CREATE TABLE FAIT_INDICE_PRIX (
            date_id TEXT PRIMARY KEY,
            indice_ippap REAL NOT NULL,
            FOREIGN KEY (date_id)
                REFERENCES DIM_DATE(date_id)
        );

        CREATE TABLE REF_PRIX_HISTORIQUE (
            mois INTEGER PRIMARY KEY,
            indice_moyen REAL NOT NULL
        );
    """)

    # 7. Chargement des données
    fait_consommation.to_sql(
        "FAIT_CONSOMMATION",
        conn,
        if_exists="append",
        index=False
    )

    fait_prix.to_sql(
        "FAIT_INDICE_PRIX",
        conn,
        if_exists="append",
        index=False
    )

    ref_historique.to_sql(
        "REF_PRIX_HISTORIQUE",
        conn,
        if_exists="append",
        index=False
    )

    # 8. Vérification des tables
    print("\nVERIFICATION DES NOUVELLES TABLES")

    tables = [
        "FAIT_CONSOMMATION",
        "FAIT_INDICE_PRIX",
        "REF_PRIX_HISTORIQUE"
    ]

    for table in tables:
        nombre = conn.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        print(f"{table} : {nombre} lignes")

    # 9. Vérification des relations
    erreurs = conn.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    assert not erreurs, erreurs

    # 10. Validation métier
    resultat = conn.execute("""
        SELECT consommation_milliers_tec
        FROM FAIT_CONSOMMATION
        WHERE date_id = '2026-06-01'
    """).fetchone()

    assert round(resultat[0], 1) == 189.4

    resultat = conn.execute("""
        SELECT indice_ippap
        FROM FAIT_INDICE_PRIX
        WHERE date_id = '2026-07-01'
    """).fetchone()

    assert round(resultat[0], 1) == 126.7

print("\nINTEGRATION SQL : OK")
print("VALIDATION METIER : OK")