import sqlite3
import spacy
import fr_core_news_md
import re
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

from sklearn.cluster import KMeans
import pandas as pd
from sklearn.decomposition import PCA
import plotly.express as px
from collections import Counter
import numpy as np
from sklearn.preprocessing import normalize

import networkx as nx
from sklearn.metrics.pairwise import linear_kernel
from pyvis.network import Network

nlp = fr_core_news_md.load()

def compute_spacy_similarity(cur):
    texts = corpus(cur, "RECETTES")
    vectors = spacy_vectors(texts) 
    matrix = np.vstack(vectors)
    matrix = normalize(matrix)
    
    cosine_sim = linear_kernel(matrix, matrix)

    titles = [t[0] for t in cur.execute("SELECT titre FROM RECETTES").fetchall()]

    return cosine_sim, titles

def recommend_similar(cur, recipe_index, cosine_sim, titles, top_n=3):
    sims = cosine_sim[recipe_index]
    indices = sims.argsort()[::-1][1: top_n+1]  
    recommendations = [(titles[i], sims[i]) for i in indices]
    return recommendations



def corpus(cur,table): 
    query = """
        SELECT 
            r.etapes_norm,
            r.difficulte,
            r.cout,
            GROUP_CONCAT(i.ingredient, ', ') AS ingredients
        FROM RECETTES r
        LEFT JOIN LIEN_RECETTES_INGREDIENTS lri ON r.id = lri.recette_id
        LEFT JOIN INGREDIENTS i ON i.id = lri.ingredient_id
        GROUP BY r.id
    """
    corpus=cur.execute(query).fetchall()
    L = []
    for etape, diff, cout, ingredients in corpus:
        texte_complet = f"{etape} {diff} {cout} {ingredients}"
        L.append(texte_complet)
    return L


def nb_personne(t):
    personne=[int(num) for num in re.findall(r'\d+', str(t))]
    if len(personne)==0:
        portion=1
    else:
        portion=max(personne)
    if portion>13:
        portion=portion/10
    return min(portion,15)

def min_moyen(c):
    time=convert_time(c[0])
    personne= nb_personne(c[1])
    return time

def convert_time(txt):
    if txt=='' or txt==None:
        return 1
    nb=0
    txt=txt.replace(' ','')
    txt=txt.replace('H','h')
    jours = re.search(r'(\d+)\s*j', txt)
    heures = re.search(r'(\d{2})\s*h', txt)
    minutes = re.search(r'(\d{2})\s*min', txt)
    if jours:
        nb += int(jours.group(1)) * 1440
    if heures:
        nb += int(heures.group(1)) * 60
    if minutes:
        nb += int(minutes.group(1))
    return nb

def apply_poid(df,lst_pd):
    df = df.mul(pd.Series(lst_pd), axis=0)
    return df

def apply_poid_after_tfidf(X,lst_pd):
    for i in range (len(X)):
        X[i]=X[i]*lst_pd[i]
    return X

def tfidf(corpus):

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus)

    return(X.toarray())



def spacy_vectors(corpus):
    docs = list(nlp.pipe(corpus))  
    vectors = [doc.vector for doc in docs]
    return vectors

# Chargement des données
def graphe_tendance(cur, table,modèle,poids):
    """créer une représentation graphique en 2D. Prend en entrer le lien vers la base, le nom de la table, et un booléen optionelle indiquant si l'ont souhaite utiliser spacy pu tfidf"""
    if not modèle:
        df = pd.DataFrame(tfidf(corpus(cur,table)))
    else:
        #utilisation de spaCy
        vectors = spacy_vectors(corpus(cur, table))
        # Convertit proprement en matrice float 2D
        matrix = np.vstack(vectors).astype(float)
        df = pd.DataFrame(matrix)

    """Pour appliquer un poids. De base, prend le temps de cuuisson"""
    if poids:
        lst_pd=[min_moyen(c) for c in cur.execute("SELECT temps_cuisson,nombre FROM RECETTES").fetchall()]
        df=apply_poid(df,lst_pd)


    X = df.select_dtypes(include=['float64', 'int64'])

    # PCA réduction à 2 dimensions
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)
    #X_pca=apply_poid_after_tfidf(X_pca,lst_pd)

    # KMeans 
    kmeans = KMeans(n_clusters=4, random_state=42)
    clusters = kmeans.fit_predict(X_pca)

    valeurs={'bon marché':2 , 'moyen':4, 'assez cher':8}


    df['PC1'] = X_pca[:, 0]
    df['PC2'] = X_pca[:, 1]
    df['Cluster'] = clusters
    df['Titre']=cur.execute("SELECT titre FROM RECETTES").fetchall()
    df['Cout']=[c[0] for c in cur.execute("SELECT cout FROM RECETTES").fetchall()]
    df['Cout_value']=df['Cout'].map(valeurs).fillna(2)
    df['dure']=[c[0] for c in cur.execute("SELECT temps_cuisson FROM RECETTES").fetchall()]
    df['Categorie'] = [c[0] for c in cur.execute("SELECT categorie FROM RECETTES").fetchall()]

    fig = px.scatter(
        df,
        x='PC1',
        y='PC2',
        color='Cluster',
        color_continuous_scale=[ "red","green","blue","purple"],
        size_max= 8,
        size= 'Cout_value',
        hover_data=['Titre','dure','Categorie'],  # infos affichées au survol
        title="Projection PCA 2D Recettes Marmiton avec spacy"
    )
    fig.show()





def graphe(cur, table,modèle,poids):
    if not modèle:
        df = pd.DataFrame(tfidf(corpus(cur,table)))
    else:
        #utilisation de spaCy
        vectors = spacy_vectors(corpus(cur, table))
        # Convertit proprement en matrice float 2D
        matrix = np.vstack(vectors).astype(float)
        df = pd.DataFrame(matrix)

    if poids:
        lst_pd=[min_moyen(c) for c in cur.execute("SELECT temps_cuisson,nombre FROM RECETTES").fetchall()]
        df=apply_poid(df,lst_pd)
    
    #print(df)
    X = df.select_dtypes(include=['float64', 'int64'])

    cosine_sim = linear_kernel(X, X)
    df['Titre']=cur.execute("SELECT titre FROM RECETTES").fetchall()
    categories = [c[0] for c in cur.execute("SELECT categorie FROM RECETTES").fetchall()]
    G=nx.Graph()
    for i, titre in enumerate(df['Titre']):
        cat = categories[i]
        G.add_node(
            i,
            label=titre[0],
            title=f"{titre[0]}<br>Catégorie : {cat}"
        )



    #Attention, ne pas mettre un seuil <0.3
    seuil = 0.35

    rows, cols = cosine_sim.shape

    #Les lignes commentées ne doivent pas être décommentées, c'est un essai non fructueux de rendre le graphe connexe
    for i in range(rows):
#        m=0
#        (a,b)=(0,0)
        for j in range(i + 1,cols):
            sim_score = cosine_sim[i, j]
            if sim_score > seuil:
                G.add_edge(i, j, value=float(sim_score), title=f"Similitude: {sim_score:.2f}")
#            if sim_score>m:
#               m=sim_score
#                (a,b)=(i,j)
#            G.add_edge(a, b, value=float(m), title=f"Similitude: {m:.2f}")

    net=Network(height="750px", width="100%", bgcolor="#222222", font_color="white", select_menu=True, cdn_resources='remote')
    net.from_nx(G)
    net.save_graph("graphe_recettes.html")


import plotly.graph_objects as go

def graphe_plotly(cur, table,idf=True):
    if idf:
        df = pd.DataFrame(tfidf(corpus(cur,table)))
    else:
        #utilisation de spaCy
        vectors = spacy_vectors(corpus(cur, table))
        # Convertit proprement en matrice float 2D
        matrix = np.vstack(vectors).astype(float)
        df = pd.DataFrame(matrix)

    #print(df)
    X = df.select_dtypes(include=['float64', 'int64'])
 

    cosine_sim = linear_kernel(X, X)
    df['Titre']=cur.execute("SELECT titre FROM RECETTES").fetchall()
    G=nx.Graph()
    for i,titre in enumerate(df['Titre']):
        G.add_node(i, label=titre, title=str(titre[0]))


    #Attention, ne pas mettre un seuil <0.3
    seuil = 0.35

    rows, cols = cosine_sim.shape
    
    for i in range(rows):
        for j in range(i + 1,cols):
            sim_score = cosine_sim[i, j]
            if sim_score > seuil: 
                G.add_edge(i, j, value=float(sim_score), title=f"Similitude: {sim_score:.2f}")

    

    pos = nx.spring_layout(G, seed=42)

    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    node_text = []
        
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(G.nodes[node]['title'])

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text, # texte qui s'affiche au survol
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=10,
            line_width=2))

    # assemblage de la figure
    fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    title='Réseau de similarité des recettes',
            #        title_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
        #fig.show()
    fig.write_html("graphe2.html")


