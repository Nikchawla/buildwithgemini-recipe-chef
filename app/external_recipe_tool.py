"""External public recipe API tool using TheMealDB."""

import json
import os
import urllib.parse
import urllib.request


def search_online_recipes(query: str) -> str:
    """Search for real recipes from a free global public recipe database (TheMealDB).

    Args:
        query: Name of a dish or ingredient to search for online (e.g. 'pasta', 'tacos', 'salmon', 'curry').

    Returns:
        Formatted summary of real recipes found online, including ingredients and instructions.
    """
    api_key = os.environ.get("THEMEALDB_API_KEY", "1")
    encoded_query = urllib.parse.quote(query.strip())
    url = f"https://www.themealdb.com/api/json/v1/{api_key}/search.php?s={encoded_query}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "RecipeChef/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        meals = data.get("meals")
        if not meals:
            return f"No online recipes found matching query '{query}'."

        results = []
        for meal in meals[:3]:  # Top 3 matching results
            title = meal.get("strMeal", "Untitled")
            category = meal.get("strCategory", "General")
            area = meal.get("strArea", "International")
            instructions = meal.get("strInstructions", "")
            instructions_snippet = (instructions[:220] + "...") if len(instructions) > 220 else instructions
            thumb = meal.get("strMealThumb", "")

            # Extract ingredients and measurements
            ingredients = []
            for i in range(1, 21):
                ing = meal.get(f"strIngredient{i}")
                meas = meal.get(f"strMeasure{i}")
                if ing and ing.strip():
                    measure_str = f"{meas.strip()} " if meas and meas.strip() else ""
                    ingredients.append(f"{measure_str}{ing.strip()}")

            results.append(
                f"=== {title} ({category} | {area} Cuisine) ===\n"
                f"Ingredients: {', '.join(ingredients[:8])}\n"
                f"Instructions Preview: {instructions_snippet}\n"
                f"Thumbnail URL: {thumb}"
            )

        return f"Found {len(results)} online recipe(s) for '{query}':\n\n" + "\n\n".join(results)

    except Exception as e:
        return f"Error fetching online recipes for '{query}': {str(e)}"
