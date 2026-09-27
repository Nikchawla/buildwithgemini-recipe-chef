"""Firestore database tools for the recipe-chef agent."""

from google.cloud import firestore

# CRITICAL: Hardcode project ID as string for Firestore client.
# Do NOT use google.auth.default() or GOOGLE_CLOUD_PROJECT env var on Agent Platform.
PROJECT_ID = "qwiklabs-gcp-03-6c3aab0d52d4"


def _get_firestore_client():
    return firestore.Client(project=PROJECT_ID)


def search_recipes(
    query: str = "", cuisine: str = "", dietary_tag: str = ""
) -> str:
    """Search and filter recipes in the Firestore database.

    Args:
        query: Optional text to match against recipe titles or ingredients.
        cuisine: Optional cuisine filter (e.g. 'Italian', 'Thai', 'Indian').
        dietary_tag: Optional dietary tag (e.g. 'vegetarian', 'vegan', 'gluten-free', 'nut-free').

    Returns:
        A list of matching recipe summaries.
    """
    db = _get_firestore_client()
    recipes_ref = db.collection("recipes")

    docs = recipes_ref.stream()
    matches = []

    q_lower = query.lower().strip() if query else ""
    c_lower = cuisine.lower().strip() if cuisine else ""
    d_lower = dietary_tag.lower().strip() if dietary_tag else ""

    for doc in docs:
        data = doc.to_dict()
        doc_id = doc.id
        title = data.get("title", "")
        doc_cuisine = data.get("cuisine", "")
        tags = [t.lower() for t in data.get("dietary_tags", [])]
        ingredients = [i.lower() for t in data.get("ingredients", []) for i in ([t] if isinstance(t, str) else [])]

        # Filter by cuisine
        if c_lower and c_lower not in doc_cuisine.lower():
            continue

        # Filter by dietary tag
        if d_lower and d_lower not in tags:
            continue

        # Filter by query text (title or ingredients)
        if q_lower:
            title_match = q_lower in title.lower()
            ing_match = any(q_lower in ing for ing in ingredients)
            if not (title_match or ing_match):
                continue

        matches.append({
            "id": doc_id,
            "title": title,
            "cuisine": doc_cuisine,
            "prep_time_mins": data.get("prep_time_mins", 0),
            "cook_time_mins": data.get("cook_time_mins", 0),
            "difficulty": data.get("difficulty", "Unknown"),
            "calories_per_serving": data.get("calories_per_serving", 0),
            "dietary_tags": data.get("dietary_tags", []),
        })

    if not matches:
        return "No recipes found matching your criteria."

    result = f"Found {len(matches)} recipe(s):\n"
    for r in matches:
        result += (
            f"- [{r['id']}] {r['title']} ({r['cuisine']}) | "
            f"Prep: {r['prep_time_mins']}m, Cook: {r['cook_time_mins']}m | "
            f"Difficulty: {r['difficulty']} | "
            f"Tags: {', '.join(r['dietary_tags']) if r['dietary_tags'] else 'None'}\n"
        )

    return result.strip()


def get_recipe(recipe_id: str) -> str:
    """Retrieve complete details for a specific recipe by ID.

    Args:
        recipe_id: The unique identifier of the recipe (e.g. 'spaghetti-carbonara').

    Returns:
        Complete recipe details including ingredients and instructions.
    """
    db = _get_firestore_client()
    doc_ref = db.collection("recipes").document(recipe_id)
    doc = doc_ref.get()

    if not doc.exists:
        return f"Recipe with ID '{recipe_id}' not found in database."

    data = doc.to_dict()
    title = data.get("title", "Untitled Recipe")
    cuisine = data.get("cuisine", "General")
    prep_time = data.get("prep_time_mins", 0)
    cook_time = data.get("cook_time_mins", 0)
    difficulty = data.get("difficulty", "Unknown")
    calories = data.get("calories_per_serving", 0)
    tags = ", ".join(data.get("dietary_tags", [])) or "None"
    ingredients = data.get("ingredients", [])
    instructions = data.get("instructions", [])

    out = f"=== {title} ({recipe_id}) ===\n"
    out += f"Cuisine: {cuisine}\n"
    out += f"Prep Time: {prep_time} mins | Cook Time: {cook_time} mins | Difficulty: {difficulty}\n"
    out += f"Calories: {calories} kcal/serving | Dietary Tags: {tags}\n\n"

    out += "Ingredients:\n"
    for ing in ingredients:
        out += f"- {ing}\n"

    out += "\nInstructions:\n"
    for idx, step in enumerate(instructions, 1):
        out += f"{idx}. {step}\n"

    return out.strip()


def add_recipe(
    recipe_id: str,
    title: str,
    cuisine: str,
    prep_time_mins: int,
    cook_time_mins: int,
    difficulty: str,
    ingredients: list[str],
    instructions: list[str],
    calories_per_serving: int = 0,
    dietary_tags: list[str] = None,
) -> str:
    """Add a new recipe to the Firestore database.

    Args:
        recipe_id: Unique slug identifier for the recipe (e.g. 'lemon-garlic-chicken').
        title: Title of the recipe.
        cuisine: Cuisine style (e.g. 'Italian', 'Mexican', 'Asian').
        prep_time_mins: Preparation time in minutes.
        cook_time_mins: Cooking time in minutes.
        difficulty: Difficulty level (e.g. 'Easy', 'Medium', 'Hard').
        ingredients: List of ingredient strings.
        instructions: List of step-by-step instruction strings.
        calories_per_serving: Estimated calories per serving.
        dietary_tags: Optional list of dietary tags (e.g. ['gluten-free', 'keto']).

    Returns:
        Confirmation message.
    """
    db = _get_firestore_client()
    doc_ref = db.collection("recipes").document(recipe_id)

    recipe_data = {
        "id": recipe_id,
        "title": title,
        "cuisine": cuisine,
        "prep_time_mins": prep_time_mins,
        "cook_time_mins": cook_time_mins,
        "difficulty": difficulty,
        "ingredients": ingredients,
        "instructions": instructions,
        "calories_per_serving": calories_per_serving,
        "dietary_tags": dietary_tags or [],
    }

    doc_ref.set(recipe_data)
    return f"Successfully added recipe '{title}' (ID: {recipe_id}) to Firestore."
