# Marmiton Recipe Mining & Semantic Network

Projet universitaire d'ingénierie des données et de traitement automatique du langage naturel (NLP) réalisé dans le cadre de la troisième année de Licence (L3).

Ce projet implémente un pipeline complet : web scraping de données culinaires, stockage relationnel normalisé, vectorisation textuelle, réduction de dimension, clustering, graphes interactifs de similarité et moteur de recommandation de recettes selon les ingrédients disponibles[cite: 38, 39, 41, 42].

---

## Auteurs
- Cyrian Revel-Hidalgo
- Oliver Warde
- Guillaume Renaud

---

## Fonctionnalités

- **Scraping et structuration des données (`ScrapingMarmiton.py`)**[cite: 42] :
  - Extraction récursive sur Marmiton (titres, ingrédients, quantités, temps de préparation/cuisson/repos, étapes, portions, difficulté, coût)[cite: 42].
  - Classification heuristique automatique des recettes : *entrée*, *plat*, *dessert*[cite: 42, 43].
  - Base SQLite normalisée à trois tables : `RECETTES`, `INGREDIENTS` et table d'association `LIEN_RECETTES_INGREDIENTS`[cite: 42].
- **Prétraitement NLP et vectorisation (`tfidf.py`)**[cite: 38, 42] :
  - Lemmatisation, suppression de la ponctuation et des stopwords via le modèle `fr_core_news_md` de spaCy[cite: 38, 42].
  - Comparaison entre deux représentations vectorielles : **TF-IDF** (sac de mots) et **plongements spaCy** (moyenne de vecteurs)[cite: 38].
  - Pondération configurable selon la durée de cuisson[cite: 38].
- **Clustering et analyse non supervisée (`tfidf.py`)**[cite: 38] :
  - Réduction de dimension en 2D via **PCA**[cite: 38].
  - Regroupement des recettes en 4 clusters via **K-Means**[cite: 38].
  - Visualisation interactive avec Plotly Express[cite: 38].
- **Graphes de similarité (`tfidf.py`)**[cite: 38] :
  - Calcul de la matrice de similarité cosinus entre recettes[cite: 38].
  - Modélisation de réseau avec **NetworkX** (seuil de similarité >= 0.35)[cite: 38].
  - Export web interactif via **PyVis** (`graphe_recettes.html`) et **Plotly** (`graphe2.html`)[cite: 38].
- **Moteur de recherche et recommandation (`search.py`, `RecipeFinder.py`)**[cite: 38, 39, 43] :
  - Interface console : saisie libre d'ingrédients[cite: 39].
  - Matching de la meilleure recette selon les correspondances d'ingrédients et de titre[cite: 43].
  - Recommandation connexe des recettes les plus similaires sémantiquement[cite: 38, 39].

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
Pour initialiser ou alimenter la base SQLite `baseDonnees.db` (remplacer `50` par le nombre souhaité)[cite: 41] :
```bash
python main.py scraping 50
```

### 2. Visualisation 2D (PCA + K-Means)
Pour ouvrir le graphique interactif Plotly[cite: 38, 41] :
```bash
# Version standard TF-IDF
python main.py graphique

# Version avec vecteurs spaCy et pondération par le temps de cuisson
python main.py graphique modele=spacy poids=True
```

### 3. Graphe de similarité (Réseau interactif)
Pour générer le fichier HTML du graphe de similarité[cite: 38, 41] :
```bash
# Export interactif PyVis (graphe_recettes.html)
python main.py graphe modele=spacy
```
Le fichier `graphe_recettes.html` s'ouvre directement dans n'importe quel navigateur web[cite: 38].

### 4. Recherche et recommandation de recettes
Pour lancer l'assistant dans le terminal[cite: 39] :
```bash
python search.py
```
Entrez vos ingrédients séparés par des virgules (ex. `tomate, mozzarella, basilic`) pour obtenir la recette correspondante ainsi que les suggestions proches[cite: 39].

---

## Technologies Utilisées

- Langage : Python[cite: 38, 39, 41, 42, 43]
- Base de données : SQLite3[cite: 38, 39, 41, 42, 43]
- Scraping : Requests, BeautifulSoup4[cite: 40, 42]
- Traitement du langage naturel (NLP) : spaCy (fr_core_news_md), Scikit-learn (TF-IDF)[cite: 38, 40, 42]
- Machine Learning non supervisé : K-Means, PCA[cite: 38]
- Graphes & Visualisation : NetworkX, PyVis, Plotly[cite: 38, 40]
