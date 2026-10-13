
from pathlib import Path
import sqlite3
import pandas as pd

# Connexion à notre base SQL
projet = Path(__file__).resolve().parent.parent
base = projet / "04_SQL" / "smart_bi_volaille.db"

if not base.exists():
    raise FileNotFoundError("Base SQL introuvable.")

with sqlite3.connect(base) as connexion:

    # REQUETE 1 : Évolution des abattages
    requete1 = """
    SELECT
        d.annee,
        d.mois,
        ROUND(f.volume_millions_tetes, 2) AS volume
    FROM FAIT_ABATTAGES_MENSUELS f
    INNER JOIN DIM_DATE d
        ON f.date_id = d.date_id
    WHERE d.mois = 7
    ORDER BY d.annee;
    """

    resultat1 = pd.read_sql_query(
        requete1, connexion
    )

    print("EVOLUTION DES ABATTAGES")
    print(resultat1.to_string(index=False))

    # REQUETE 2 : Volumes par espèce
    requete2 = """
    SELECT
        e.nom_espece,
        ROUND(f.volume_millions_tetes, 2)
            AS volume_millions,
        ROUND(f.evolution_annuelle_pct, 1)
            AS evolution_pct
    FROM FAIT_ABATTAGES_ESPECES f
    INNER JOIN DIM_ESPECE e
        ON f.espece_id = e.espece_id
    WHERE f.date_id = '2026-07-01'
    ORDER BY f.volume_millions_tetes DESC;
    """

    resultat2 = pd.read_sql_query(
        requete2, connexion
    )

    print("\nVOLUMES PAR ESPECE")
    print(resultat2.to_string(index=False))