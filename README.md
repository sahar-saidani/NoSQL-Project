# NoSQL Data Pipeline Project

Projet ETL simple pour :

1. faire du web scraping,
2. transformer ces donnees dans un format commun,
3. les charger dans MongoDB,
4. puis dans Cassandra,
5. puis dans Neo4j.

Le projet est volontairement simple a lancer et facile a presenter.

## Architecture

- `Web scraping source` : catalogue de livres depuis `books.toscrape.com`
- `MongoDB local` : stockage documentaire des objets normalises, accessible via MongoDB Compass
- `Cassandra` : stockage denormalise pour lecture rapide
- `Neo4j` : relations entre `Item`, `Category`, `Producer` et `Source`

## Structure

```text
src/
  extractors/
    web_source.py
  loaders/
    cassandra_loader.py
    mongo_loader.py
    neo4j_loader.py
  config.py
  main.py
  models.py
  transformers.py
docker-compose.yml
requirements.txt
.env.example
```

## Installation

### 1. Creer un environnement virtuel

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Python `3.13` est accepte, a condition d'utiliser une version recente de `cassandra-driver`.

### 2. Configurer les variables d'environnement

```powershell
Copy-Item .env.example .env
```

MongoDB n'est pas lance par Docker Compose dans cette version.
La connexion attendue est en local :

```env
MONGO_URI=mongodb://localhost:27017
```

### 3. Lancer les bases NoSQL avec Docker

```powershell
docker compose up -d
```

Cette commande lance uniquement `Cassandra` et `Neo4j`.

## Execution

### Charger des livres depuis le web scraping

```powershell
python -m src.main --limit 30
```

### Extraire sans charger dans les bases

```powershell
python -m src.main --limit 10 --extract-only
```

## Donnees chargees

### MongoDB

- Base : `nosql_project`
- Collection : `items`
- Connexion locale conseillee : `mongodb://localhost:27017`

### Cassandra

- Keyspace : `nosql_project`
- Table : `catalog_items`

### Neo4j

- Noeuds : `Item`, `Category`, `Producer`, `Source`
- Relations :
  - `(:Item)-[:BELONGS_TO]->(:Category)`
  - `(:Item)-[:PRODUCED_BY]->(:Producer)`
  - `(:Item)-[:INGESTED_FROM]->(:Source)`

## Exemple de requetes

### MongoDB

```javascript
use nosql_project
db.items.find({ category: "Travel" })
```

### Cassandra

```sql
SELECT * FROM nosql_project.catalog_items;
```

### Neo4j

```cypher
MATCH (i:Item)-[:BELONGS_TO]->(c:Category)
RETURN i.name, c.name
LIMIT 20;
```

## Remarques

- `books.toscrape.com` est un site de demonstration concu pour le scraping.
- Le pipeline peut etre etendu vers d'autres sources plus proches de votre sujet.
