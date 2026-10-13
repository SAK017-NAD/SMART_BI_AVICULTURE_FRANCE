# SMART BI — Observatoire de la filière avicole française

Projet Data / Business Intelligence end-to-end réalisé à partir de données publiques Agreste sur la filière avicole française.

L’objectif de ce projet est de construire une solution Business Intelligence complète permettant de transformer des données publiques Agreste sur la filière avicole française en informations fiables, structurées et facilement exploitables pour l’analyse et la prise de décision.

Le projet couvre l’ensemble de la chaîne de traitement de la donnée, depuis les fichiers sources jusqu’à la restitution finale dans Power BI.


> Ce projet personnel utilise uniquement des données publiques Agreste.  

---

## Objectifs du projet

Le projet vise à :

- extraire automatiquement les données issues des fichiers Excel Agreste ;
- fiabiliser les données grâce à des contrôles de qualité portant notamment sur les valeurs manquantes, les doublons, la cohérence des dates et les volumes ;
- comparer les résultats calculés avec les chiffres publiés dans les rapports officiels Agreste afin de valider la cohérence des données ;
- structurer les données dans une base SQLite selon une logique de dimensions et de tables de faits ;
- automatiser le pipeline de traitement avec Python afin de rendre le processus reproductible ;
- préparer et consolider les données dans Power Query pour répondre aux différents besoins d’analyse ;
- créer des indicateurs DAX permettant de suivre les volumes d’abattage, la consommation, les prix et leurs évolutions ;
- construire des dashboards Power BI interactifs permettant d’analyser les tendances globales de la filière ainsi que les différences entre espèces de volailles.


La solution permet notamment de répondre à plusieurs questions métier :

- Comment évoluent les volumes d’abattage entre 2025 et 2026 ?
- Quelles espèces représentent les volumes les plus importants ?
- Quelles espèces connaissent les plus fortes hausses ou baisses ?
- Comment évolue la consommation de viande de volailles ?
- Comment évoluent les prix à la production ?
- Quels sont les principaux écarts entre les périodes observées ?

L’objectif final est donc de démontrer une démarche Data / BI de bout en bout : collecte, contrôle, transformation, modélisation, automatisation, analyse et restitution des données dans un outil décisionnel.


---

## Sources de données

Les données utilisées proviennent des publications officielles Agreste relatives à l’aviculture française.

Deux sources principales sont utilisées :

- fichier Excel détaillé contenant les données mensuelles ;
- publication PDF Agreste utilisée comme référentiel de validation.

Périodes principalement analysées :

- 2025 ;
- janvier à juillet 2026 selon les indicateurs.

---

## Architecture du projet

```text
SMART_BI_AVICULTURE_FRANCE/
│
├── 01_DONNEES_BRUTES/
│   ├── fichier Excel Agreste
│   └── publication PDF Agreste
│
├── 02_SCRIPTS_PYTHON/
│   ├── 01_extraction_agreste.py
│   ├── 02_controles_qualite.py
│   ├── 03_validation_officielle.py
│   ├── 04_extraction_especes.py
│   ├── 05_creation_base_sql.py
│   ├── 06_analyse_sql.py
│   ├── 07_extraction_consommation.py
│   ├── 08_extraction_prix.py
│   ├── 09_integration_sql.py
│   └── 10_pipeline_complet.py
│
├── 03_DONNEES_TRAITEES/
│
├── 04_SQL/
│
├── 05_POWER_BI/
│   ├── EXPORTS/
│   └── SCREENSHOTS/
│
├── 06_PRESENTATION/
│
├── .gitignore
├── requirements.txt
└── README.md
```

## Pipeline Python

Le traitement est organisé en 10 scripts Python.

### 01 — Extraction des abattages

Extraction des volumes mensuels d’abattage depuis le fichier Excel Agreste.

Création d’un fichier structuré contenant notamment :

- date ;
- année ;
- mois ;
- volume d’abattage en millions de têtes.

### 02 — Contrôles qualité

Mise en place de contrôles automatiques :

- valeurs manquantes ;
- doublons ;
- cohérence des dates ;
- contrôle des volumes ;
- cohérence année / mois.

### 03 — Validation officielle

Comparaison des résultats calculés avec les chiffres publiés dans le PDF officiel Agreste.

Exemple :

- abattages juillet 2026 : environ 73 millions de têtes ;
- évolution annuelle : environ -1,6 %.

### 04 — Extraction par espèce

Extraction des volumes d’abattage par espèce :

- poulets ;
- dindes ;
- canards à rôtir ;
- canards à gaver ;
- pintades ;
- poules de réforme ;
- autres catégories disponibles dans la source.

### 05 — Création de la base SQL

Création d’une base SQLite permettant de structurer les données.

Principales tables :

- `DIM_DATE`
- `DIM_ESPECE`
- `FAIT_ABATTAGES_MENSUELS`
- `FAIT_ABATTAGES_ESPECES`

### 06 — Analyse SQL

Exécution de requêtes SQL permettant de contrôler et analyser les données stockées.

Exemples :

- comparaison juillet 2025 / juillet 2026 ;
- analyse des volumes par espèce ;
- contrôle des agrégations.

### 07 — Extraction de la consommation

Extraction de la consommation apparente mensuelle de viande de volailles.

Exemple :

- juin 2026 : environ 189,4 milliers de tonnes équivalent carcasse.

### 08 — Extraction des prix

Extraction de l’indice IPPAP des prix à la production des volailles.

Exemple :

- juillet 2026 : indice 126,7 ;
- base 100 en 2020.

### 09 — Intégration SQL

Ajout des nouvelles données dans la base SQLite :

- consommation ;
- indice des prix ;
- références historiques.

### 10 — Pipeline complet

Automatisation de l’ensemble du processus :

1. extraction ;
2. nettoyage ;
3. contrôles qualité ;
4. validation ;
5. alimentation SQL ;
6. génération des fichiers destinés à Power BI.

---

## Exports Power BI

Le pipeline génère plusieurs fichiers utilisés dans Power BI :

```text
DIM_DATE.csv
DIM_ESPECE.csv
FAIT_ABATTAGES_MENSUELS.csv
FAIT_ABATTAGES_ESPECES.csv
FAIT_CONSOMMATION.csv
FAIT_INDICE_PRIX.csv
REF_PRIX_HISTORIQUE.csv
```

---

## Power Query

Les données sont consolidées dans Power Query afin de créer deux tables principales de reporting.

### REPORTING MENSUEL

Table utilisée pour l’analyse :

- des abattages ;
- de la consommation ;
- de l’indice des prix ;
- des tendances mensuelles.

### REPORTING ESPECES

Table utilisée pour analyser :

- les volumes par espèce ;
- les évolutions annuelles ;
- les écarts par rapport aux références historiques.

Les deux tables possèdent des grains différents afin d’éviter les doublons et les erreurs d’agrégation.

---

## Power BI

Le rapport Power BI comporte trois pages.

### 1 — Vue d’ensemble du marché avicole

Principaux indicateurs :

- abattages ;
- consommation ;
- indice des prix ;
- évolutions annuelles.

### 2 — Analyse des abattages par espèce

Analyse détaillée :

- volume total ;
- volume de poulets ;
- plus forte hausse ;
- plus forte baisse ;
- volumes par espèce ;
- évolution annuelle par espèce.

### 3 — Analyse marché & tendances

Analyse croisée :

- évolution des prix ;
- consommation ;
- tendances 2025 / 2026 ;
- synthèse mensuelle des indicateurs.

---

## Exemples de KPI

| Indicateur | Valeur |
|---|---:|
| Abattages juillet 2026 | 72,98 M |
| Évolution annuelle des abattages | -1,6 % |
| Consommation juin 2026 | 189,4 K tec |
| Évolution annuelle de la consommation | +3,9 % |
| Indice prix juillet 2026 | 126,7 |
| Évolution annuelle des prix | +2,2 % |

---

## Technologies utilisées

- Python
- Pandas
- Excel
- SQLite
- SQL
- Power Query
- Power BI
- DAX
- Visual Studio Code
- Git / GitHub

---

## Compétences démontrées

Ce projet illustre une démarche Data / BI complète :

- compréhension du besoin métier ;
- extraction et transformation des données ;
- automatisation Python ;
- Data Quality ;
- validation des données ;
- SQL et modélisation ;
- préparation Power Query ;
- création de KPI DAX ;
- Data Visualisation ;
- restitution métier.

---

## Auteur

**Nadiath SAKA**

Data / Business Analyst  
Power BI · Python · SQL · Data Quality