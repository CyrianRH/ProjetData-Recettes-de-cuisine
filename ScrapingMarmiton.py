import requests
from bs4 import BeautifulSoup
import re
import sqlite3
import spacy
import fr_core_news_md
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

import pandas as pd
from sklearn.decomposition import PCA
import plotly.express as px
from RecipeFinder import classify_recipe


"""
url_test = "https://www.marmiton.org/recettes/recette_poulet-au-coco-et-curry_17803.aspx"
url_test2 = "https://www.marmiton.org/recettes/recette_couscous-royal-agneau-poulet-merguez_36674.aspx"

"""
url ="https://www.marmiton.org/qu-est-ce-qu-on-mange-ce-soir-sc29.html"


def get_text_if_not_none(e):
    if e:
        return e.text.strip()
    return None


def open_url(url):
    r=requests.get(url)
    if r.status_code == 200:
        html = r.text

        with open("recette.html", "w", encoding='utf-8') as f:
            f.write(html)

        soup = BeautifulSoup(html, "html.parser")
        return soup
    return None


#Titre
def titre(soup):
    titre = get_text_if_not_none(soup.find("h1"))
    return titre


#Nbr personnes
def nbr(soup):
    nbr = None
    #récupère tout les classe qui on script type="application&#x2F;ld&#x2B;json"
    jsonld_scripts = soup.find_all("script", {"type": "application/ld+json"})

    for text in jsonld_scripts:
        if "recipeYield" in text.string:
            result = re.search(r'"recipeYield":"(.*?)"', text.string)
            nbr=result.group(1)
    return nbr

#Liste ingrédients et quantités
def ingredients_quantites(soup):
    ingredients = []
    quantites = []

    card_ingredients = soup.select(".card-ingredient")
    for card in card_ingredients:
        # quantité
        q = None
        q_span = card.select_one(".card-ingredient-quantity")
        count = get_text_if_not_none(q_span.select_one(".count"))
        unit = get_text_if_not_none(q_span.select_one(".unit"))
        if count:
            q = (count + (" " + unit if unit else "")).strip()
        # nom ingrédient
        name = None
        name_span = card.select_one(".ingredient-name")
        if name_span:
            name = name_span.get_text(strip=True)

        ingredients.append(name)
        quantites.append(q)
    return ingredients,quantites


#Difficulté
def difficulte(soup):
    difficulte = None
    # la difficulté est dans le deuxième .recipe-primary__item > span
    diff_span = soup.find("i", class_="icon-difficulty")
    if diff_span!=None:
        parent = diff_span.find_parent()
        difficulte = get_text_if_not_none(parent.find("span"))
    return difficulte



#Coût
def cout(soup):
    cout = None
    diff_span = soup.find("i", class_="icon-price")
    if diff_span!=None:
        parent = diff_span.find_parent()
        cout = get_text_if_not_none(parent.find("span"))
    return cout


#Temps total
def temps_total(soup):
    temps_total = None

    first_primary = soup.select_one(".recipe-primary__item span")
    temps_total = get_text_if_not_none(first_primary)
    return temps_total


#Temps de préparation
def temps_prepa(soup):
    temps_prepa = None

    first_primary = soup.select_one(".time__details div div")
    temps_prepa = get_text_if_not_none(first_primary)
    return temps_prepa


#Temps de cuisson
def temps_cuisson(soup):
    temps_cuisson = None
    cuisson_span = None

    # chercher le label "Cuisson :" puis remonter pour trouver la valeur
    for span in soup.find_all("span"):
        if span.get_text(strip=True) == "Cuisson :":
            cuisson_span = span
            break

    if cuisson_span!=None:
        parent = cuisson_span.find_parent()
        temps_cuisson = get_text_if_not_none(parent.find("div"))
    return temps_cuisson


#Temps de repos
def temps_repos(soup):
    temps_repos = None
    repos_span = None

    for span in soup.find_all("span"):
        if span.get_text(strip=True) == "Repos :":
            cuisson_span = span
            break

    if repos_span!=None:
        parent = repos_span.find_parent()
        temps_repos = get_text_if_not_none(parent.find("div"))
    return temps_repos



#Toutes les étapes en un seul texte
def etapes(soup):
    etapes_elems = soup.select(".recipe-step-list__container p")
    etapes = " ".join(e.get_text(" ", strip=True) for e in etapes_elems if e.get_text(strip=True))
    # fallback: paragraphs under .recipe-preparation
    if not etapes:
        prep_div = soup.select_one(".recipe-preparation")
        if prep_div:
            ps = prep_div.find_all("p")
            etapes = " ".join(get_text_if_not_none(p) for p in ps if get_text_if_not_none(p))
    return etapes


def récup_info(soup):
    info="TITRE : "+titre(soup)+"\n"
    info+="POUR : "+str(nbr(soup))+"\n"
    info+="LISTE DES INGREDIENTS : "+str(ingredients_quantites(soup)[0])+"\n"
    info+="QUANTITES : "+str(ingredients_quantites(soup)[1])+"\n"
    info+="DIFFICULTE : "+str(difficulte(soup))+"\n"
    info+="COUT : "+str(cout(soup))+"\n"
    info+="TEMPS TOTAL : "+str(temps_total(soup))+"\n"
    info+="TEMPS DE PREPARATION : "+str(temps_prepa(soup))+"\n"
    info+="TEMPS DE CUISSON : "+str(temps_cuisson(soup))+"\n"
    info+="TEMPS DE REPOS : "+str(temps_repos(soup))+"\n"
    info+="RECETTE : "+str(etapes(soup))+"\n"
    return info




def ajout_sql(soup,n,i,cur):
    ingredient=ingredients_quantites(soup)
    ingredients_list = ingredient[0]
    ingredients_txt = ", ".join(ingredients_list)
    categorie = classify_recipe(titre(soup), ingredients_txt)
    data=(n,categorie,titre(soup),i,nbr(soup),difficulte(soup),cout(soup),temps_total(soup),temps_prepa(soup),temps_cuisson(soup),temps_repos(soup),etapes(soup),normalisation(etapes(soup)))
    #ajoute les infos dans la table RECETTES
    cur.execute("""
    INSERT INTO RECETTES(
    id, categorie, titre, url, nombre, difficulte, cout,
    temps_total, temps_prepa, temps_cuisson, temps_repos,
    etapes, etapes_norm
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    for i in range(len(ingredient[0])):
        # parcours la liste des ingredients
        # regarde si l'ingredien fait déjà partie de la tables INGREDIENTS, et récup son ID
        cur.execute("SELECT id FROM INGREDIENTS WHERE ingredient=?", (str(ingredient[0][i]),))
        result=cur.fetchone()
        if result is None:
            # Sinon, ajoute l'ingredien a la table
            cur.execute("INSERT INTO INGREDIENTS (ingredient) VALUES (?)", (str(ingredient[0][i]),))
            cur.execute("SELECT id FROM INGREDIENTS WHERE ingredient=?", (str(ingredient[0][i]),))
            id_ingredient=cur.lastrowid
        else:
            id_ingredient=result[0]
        # fait le lien entre la recette, l'ingredient et la quantités
        # SAVOIR CE QUE L ONT FAIT SI ON A PLUSIEURS FOIS LE MÊME INGREDIENT: 
        #car dans https://www.marmiton.org/recettes/recette_baklavas-pour-tous-et-pour-tous-les-jours_30421.aspx, il y a 2 fois amandes
        cur.execute("INSERT OR IGNORE INTO LIEN_RECETTES_INGREDIENTS (recette_id,ingredient_id , quantite) VALUES (?,?,?)" , (n,id_ingredient,str(ingredient[1][i])))
    return None


def get_url_recette(soup,lst_url):
    """Fonction qui récupère tout les liens de recette qui apparaise sur une page"""
    urls = re.findall(r'"(https://www\.marmiton\.org/recettes/recette[^"]+)"', str(soup))
    for url in urls:
        if url not in lst_url:
            # l'ajoute au autre lien uniquement si il n'y est pas déjà
            lst_url.append(url)
    return lst_url

#print(get_url_recette(soup,[]))

def extract_url():
    #commence par ouvrir la page principale des recette, pour en récupérer le plus de recette possible
    soup=open_url(url)
    lst_url=[]
    if soup==None:
        return None
    get_url_recette(soup,lst_url)
    nb=0
    soup=open_url(lst_url[nb])
    return lst_url

#print(len(extract_url()))

# chargement du modele spaCy pour la langue francaise
#nlp = spacy.load("fr_core_news_sm")  #marche pas
nlp = fr_core_news_md.load()


def normalisation(input_text):
    doc = nlp(input_text)
# extraction des mots lemmatises
    lemmatized_text = " ".join([token.lemma_ for token in doc if not token.is_stop and not token.is_punct])
    return lemmatized_text

def create_table(cur):
    cur.execute("DROP TABLE IF EXISTS RECETTES")
    cur.execute("CREATE TABLE RECETTES(id INT ,categorie TXT, titre TXT,url TXT, nombre INT, difficulte TXT, cout TXT, temps_total TXT, temps_prepa TXT, temps_cuisson TXT, temps_repos TXT, etapes TXT, etapes_norm TXT)")
    cur.execute("DROP TABLE IF EXISTS INGREDIENTS")
    cur.execute("CREATE TABLE INGREDIENTS(id INTEGER PRIMARY KEY AUTOINCREMENT, ingredient TEXT)")
    cur.execute("DROP TABLE IF EXISTS LIEN_RECETTES_INGREDIENTS")
    cur.execute("CREATE TABLE LIEN_RECETTES_INGREDIENTS( recette_id INTEGER,ingredient_id INTEGER,quantite TEXT, PRIMARY KEY (recette_id, ingredient_id),FOREIGN KEY (recette_id) REFERENCES RECETTES(id) , FOREIGN KEY (ingredient_id) REFERENCES INGREDIENTS(id))")


def extract(max_recette,cur):
    create_table(cur)
    # cur.execute("DROP TABLE IF EXISTS RECETTES")
    # cur.execute("CREATE TABLE RECETTES(id INT, titre TXT,url TXT, nombre INT, ingredients TXT,quantites TXT, difficulte TXT, cout TXT, temps_total TXT, temps_prepa TXT, temps_cuisson TXT, temps_repos TXT, etapes TXT, etapes_norm TXT)")
    n=0
    lst_url=extract_url()
    while n<len(lst_url) and n<max_recette:
        print(lst_url[n])
        soup=open_url(lst_url[n])
        ajout_sql(soup,n,lst_url[n],cur)
        get_url_recette(soup,lst_url)
        n+=1
    return None


#On se déconnecte de la base sql
# conn.commit()
# cur.close()
# conn.close()


