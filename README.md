# Marmiton Recipe Mining & Semantic Network

Projet universitaire d'ingénierie des données et de traitement automatique du langage naturel (NLP) réalisé dans le cadre de la troisième année de Licence (L3).

Ce projet implémente un pipeline complet : web scraping de données culinaires, stockage relationnel normalisé, vectorisation textuelle, réduction de dimension, clustering, graphes interactifs de similarité et moteur de recommandation de recettes selon les ingrédients disponibles.

---

## Auteurs
- Cyrian Revel-Hidalgo
- Oliver Warde
- Guillaume Renaud

---

## Fonctionnalités

- **Scraping et structuration des données (`ScrapingMarmiton.py`)** :
  - Extraction récursive sur Marmiton (titres, ingrédients, quantités, temps de préparation/cuisson/repos, étapes, portions, difficulté, coût).
  - Classification heuristique automatique des recettes : *entrée*, *plat*, *dessert*.
  - Base SQLite normalisée à trois tables : `RECETTES`, `INGREDIENTS` et table d'association `LIEN_RECETTES_INGREDIENTS`.
- **Prétraitement NLP et vectorisation (`tfidf.py`)** :
  - Lemmatisation, suppression de la ponctuation et des stopwords via le modèle `fr_core_news_md` de spaCy.
  - Comparaison entre deux représentations vectorielles : **TF-IDF** (sac de mots) et **plongements spaCy** (moyenne de vecteurs).
  - Pondération configurable selon la durée de cuisson.
- **Clustering et analyse non supervisée (`tfidf.py`)** :
  - Réduction de dimension en 2D via **PCA**.
  - Regroupement des recettes en 4 clusters via **K-Means**.
  - Visualisation interactive avec Plotly Express.
- **Graphes de similarité (`tfidf.py`)** :
  - Calcul de la matrice de similarité cosinus entre recettes.
  - Modélisation de réseau avec **NetworkX** (seuil de similarité >= 0.35).
  - Export web interactif via **PyVis** (`graphe_recettes.html`) et **Plotly** (`graphe2.html`).
- **Moteur de recherche et recommandation (`search.py`, `RecipeFinder.py`)** :
  - Interface console : saisie libre d'ingrédients.
  - Matching de la meilleure recette selon les correspondances d'ingrédients et de titre.
  - Recommandation connexe des recettes les plus similaires sémantiquement.

---

## Schéma de la Base de Données

```sql
RECETTES (
    id INT, 
    categorie TXT, 
    titre TXT, 
    url TXT, 
    nombre INT, 
    difficulte TXT, 
    cout TXT, 
    temps_total TXT, 
    temps_prepa TXT, 
    temps_cuisson TXT, 
    temps_repos TXT, 
    etapes TXT, 
    etapes_norm TXT
);

INGREDIENTS (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    ingredient TEXT
);

LIEN_RECETTES_INGREDIENTS (
    recette_id INTEGER, 
    ingredient_id INTEGER, 
    quantite TEXT, 
    PRIMARY KEY (recette_id, ingredient_id),
    FOREIGN KEY (recette_id) REFERENCES RECETTES(id),
    FOREIGN KEY (ingredient_id) REFERENCES INGREDIENTS(id)
);
```

---

## Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/<votre-pseudo>/<nom-du-repo>.git
cd <nom-du-repo>
```

2. Créer et activer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate
# Sur Windows : venv\Scripts\activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Télécharger le modèle de langue spaCy :
```bash
python -m spacy download fr_core_news_md
```

---

## Utilisation

### 1. Scraping des recettes
Pour initialiser ou alimenter la base SQLite `baseDonnees.db` (remplacer `50` par le nombre souhaité) :
```bash
python main.py scraping 50
```

### 2. Visualisation 2D (PCA + K-Means)
Pour ouvrir le graphique interactif Plotly :
```bash
# Version standard TF-IDF
python main.py graphique

# Version avec vecteurs spaCy et pondération par le temps de cuisson
python main.py graphique modele=spacy poids=True
```

### 3. Graphe de similarité (Réseau interactif)
Pour générer le fichier HTML du graphe de similarité :
```bash
# Export interactif PyVis (graphe_recettes.html)
python main.py graphe modele=spacy
```
Le fichier `graphe_recettes.html` s'ouvre directement dans n'importe quel navigateur web.

### 4. Recherche et recommandation de recettes
Pour lancer l'assistant dans le terminal :
```bash
python search.py
```
Entrez vos ingrédients séparés par des virgules (ex. `tomate, mozzarella, basilic`) pour obtenir la recette correspondante ainsi que les suggestions proches.

---

## Technologies Utilisées

- Langage : Python
- Base de données : SQLite3
- Scraping : Requests, BeautifulSoup4
- Traitement du langage naturel (NLP) : spaCy (fr_core_news_md), Scikit-learn (TF-IDF)
- Machine Learning non supervisé : K-Means, PCA
- Graphes & Visualisation : NetworkX, PyVis, Plotly
