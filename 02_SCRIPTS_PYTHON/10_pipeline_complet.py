
from pathlib import Path
from datetime import datetime
import subprocess
import sys
import sqlite3
import shutil
import pandas as pd

# 1. Configuration
projet = Path(__file__).resolve().parent.parent
scripts = projet / "02_SCRIPTS_PYTHON"
dossier_sql = projet / "04_SQL"
base = dossier_sql / "smart_bi_volaille.db"

export = projet / "05_POWER_BI" / "EXPORTS"
export.mkdir(parents=True, exist_ok=True)

# 2. Fonction pour exécuter les scripts
def executer(nom):
    print(f"\nEXECUTION : {nom}", flush=True)

    subprocess.run(
        [sys.executable, str(scripts / nom)],
        cwd=projet,
        check=True
    )

    print(f"TERMINE : {nom}", flush=True)

# 3. Extraction et contrôles
etapes_extraction = [
    "01_extraction_agreste.py",
    "02_controles_qualite.py",
    "03_validation_officielle.py",
    "04_extraction_especes.py",
    "07_extraction_consommation.py",
    "08_extraction_prix.py"
]

print("DEMARRAGE DU PIPELINE")

for etape in etapes_extraction:
    executer(etape)

# 4. Sauvegarde de la base existante
sauvegarde = None

if base.exists():
    dossier_backup = dossier_sql / "SAUVEGARDES"
    dossier_backup.mkdir(exist_ok=True)

    horodatage = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    sauvegarde = (
        dossier_backup
        / f"smart_bi_{horodatage}.db"
    )

    shutil.copy2(base, sauvegarde)
    print("\nSauvegarde :", sauvegarde)

    # Reconstruction sur une nouvelle base
    base.unlink()

# 5. Reconstruction et validation SQL
try:
    executer("05_creation_base_sql.py")
    executer("06_analyse_sql.py")
    executer("09_integration_sql.py")

    # 6. Vérification de toutes les tables
    tables = {
        "DIM_DATE": 19,
        "DIM_ESPECE": 8,
        "FAIT_ABATTAGES_MENSUELS": 19,
        "FAIT_ABATTAGES_ESPECES": 8,
        "FAIT_CONSOMMATION": 18,
        "FAIT_INDICE_PRIX": 19,
        "REF_PRIX_HISTORIQUE": 12
    }

    with sqlite3.connect(base) as conn:

        erreurs = conn.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        assert not erreurs, (
            "Erreurs d'intégrité référentielle"
        )

        print("\nCONTROLE FINAL DE LA BASE")

        for table, attendu in tables.items():

            nombre = conn.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            print(f"{table} : {nombre} lignes")

            assert nombre == attendu, (
                f"Nombre incorrect pour {table}"
            )

        # 7. Préparation des exports Power BI
        for table in tables:

            df = pd.read_sql_query(
                f"SELECT * FROM {table}",
                conn
            )

            df.to_csv(
                export / f"{table}.csv",
                index=False,
                encoding="utf-8-sig"
            )

except Exception:

    print("\nECHEC DU PIPELINE SQL")

    # Restaurer la version précédente
    if base.exists():
        base.unlink()

    if sauvegarde is not None:
        shutil.copy2(sauvegarde, base)
        print("Ancienne base restaurée.")

    raise

print("\nPIPELINE TERMINE AVEC SUCCES")
print("Exports Power BI :", export)