def remove_s(w):
    if w.endswith("s"):
        return w[:-1]
    return w

def find_recipe_by_ingredients(cur, input_ingredients):
    input_set = set(i.lower().strip() for i in input_ingredients)

    query = """
        SELECT 
            r.id,
            r.titre,
            r.etapes, 
            GROUP_CONCAT(i.ingredient, ', ')
        FROM RECETTES r
        LEFT JOIN LIEN_RECETTES_INGREDIENTS l ON r.id = l.recette_id
        LEFT JOIN INGREDIENTS i ON i.id = l.ingredient_id
        GROUP BY r.id;
    """

    recipes = cur.execute(query).fetchall()

    best_score = -1
    best_recipe = None
    best_idx = None

    for idx, (recipe_id, title, steps, ing_list) in enumerate(recipes):
        if ing_list is None:
            continue

        # Ingredients match
        recipe_ing = set(ing.lower().strip() for ing in ing_list.split(", "))
        score = len(input_set & recipe_ing)

        # Title match
        title_words = title.lower().split()
        title_words_norm = [remove_s(t) for t in title_words]
        score += sum(1 for w in input_set if w in title_words_norm)

        if score > best_score:
            best_score = score
            best_recipe = (recipe_id, title, steps, ing_list, score)
            best_idx = idx


    if best_score <= 0:
        return None,None

    return best_recipe,best_idx

def classify_recipe(title, ingredients):
    title = (title or "").lower()
    ingredients = (ingredients or "").lower()

    dessert_kw = [
        "gâteau", "gateau", "tarte", "brownie", "muffin", "crème", "creme",
        "chocolat", "sucre", "miel", "glace", "caramel", "pâtisserie",
        "patisserie", "biscuit", "compote", "dessert", "vanille", "fruit"
    ]

    entree_kw = [
        "salade", "soupe", "velouté", "veloute", "tartare", "quiche",
        "toast", "bruschetta", "entrée", "entree", "apéro", "apero",
        "houmous", "rillette"
    ]

    if any(w in title or w in ingredients for w in dessert_kw):
        return "dessert"

    if any(w in title or w in ingredients for w in entree_kw):
        return "entrée"

    # Sinon plat
    return "plat"