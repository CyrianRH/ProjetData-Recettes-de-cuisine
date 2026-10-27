import sqlite3
from tfidf import *
from RecipeFinder import find_recipe_by_ingredients

conn = sqlite3.connect("baseDonnees.db")
cur = conn.cursor()


user_input = input(
    "Tu veux impressionner ton/ta partenaire avec tes talents de cuisinier ?\n"
    "Dis-moi quels ingrédients tu as (séparés par des virgules), et je te trouve LA recette qui va sauver ta soirée : "
)

cosine_sim, titles = compute_spacy_similarity(cur)

# Convert string to list
ingredients = [i.strip() for i in user_input.split(",") if i.strip()]

recipe = find_recipe_by_ingredients(cur, ingredients)

if recipe:
    best_data, index = recipe
    recipe_id, title, steps, ing_list, score = best_data

    print("Best Matching Recipe Found:")
    print("Title:", title)
    print("Matching score:", score)
    print("Matching ingredients:", ingredients)
    print("\nRecipe Ingredients:", ing_list)
    print("\nSteps:\n", steps)

    print("\n Recettes similaires recommandées:")
    sims = recommend_similar(cur, index, cosine_sim, titles)

    for i, (t, s) in enumerate(sims, 1):
        print(f"{i}. {t} (similarité: {s:.2f})")
else:
    print("No matching recipe found. Maybe did you forget to do the scrapping process of Marmyton ? There's a famous french quote that says" \
    "l'argent ne tombe pas du ciel, well guess what, recipes neither lol (humour nul d'informaticien) ")

conn.commit()
cur.close()
conn.close()