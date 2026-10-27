import sqlite3
from ScrapingMarmiton import *
from tfidf import *
import sys

#on ouvre le lien avec les tables
# conn = sqlite3.connect("baseDonnees.db")
# cur = conn.cursor()

# a décommenter 1 fois pour récupérer la base de données. 2000 c'est peu être un peu trop
# max_recette=100
# extract(max_recette,cur)


# table="RECETTES"
# graphe_tendance(cur,table)

# a décommenter pour charger le graphe avec Network, attention long à charger
#graphe(cur,table)

# graphe_plotly(cur,table)

#On se déconnecte de la base sql
# conn.commit()
# cur.close()
# conn.close()


if __name__ == "__main__":
    conn = sqlite3.connect("baseDonnees.db")
    cur = conn.cursor()
    if len(sys.argv) < 2:
        print("Il faut au moins un paramètre:\n scraping int \n graphe \n graphique")
    elif str(sys.argv[1])=="scraping":
        if len(sys.argv) == 3:
            extract(int(sys.argv[2]),cur)
        else:
            print("Avec scraping, il faut un paramètre de taille: scraping int")
    elif str(sys.argv[1])=="graphe":
        info=[False,False]
        for i in range(2,len(sys.argv)):
            if str(sys.argv[i])=="modele=spacy":
                info[0]=True
            elif str(sys.argv[i])=="poids=True":
                info[1]=True
            else:
                print("Les 2 paramètre possible sont modele=spacy et poids=True")
        graphe(cur,"RECETTES",info[0],info[1])
    elif str(sys.argv[1])=="graphique":
        info=[False,False]
        for i in range(2,len(sys.argv)):
            if str(sys.argv[i])=="modele=spacy":
                info[0]=True
            elif str(sys.argv[i])=="poids=True":
                info[1]=True
            else:
                print("Les 2 paramètre possible sont modele=spacy et poids=True")
        graphe_tendance(cur,"RECETTES",info[0],info[1])
    else:
        print("Il faut au moins un paramètre:\n scraping int \n graphe \n graphique")
    conn.commit()
    cur.close()
    conn.close()


