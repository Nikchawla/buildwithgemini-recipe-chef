"""Recipe portion and ingredient scaling tool for recipe-chef agent."""

import re


def calculate_recipe_scaling(
    ingredients: list[str],
    target_servings: int,
    base_servings: int = 4,
    calories_per_serving: int = 0,
) -> str:
    """Scale recipe ingredient amounts and calorie totals for a target number of servings.

    Args:
        ingredients: List of ingredient strings (e.g. ['200g spaghetti', '2 eggs', '100g pancetta']).
        target_servings: The desired number of servings to cook for.
        base_servings: The original recipe serving size (default 4).
        calories_per_serving: Base calories per serving (optional).

    Returns:
        Formatted string containing scaled ingredient quantities and calorie totals.
    """
    if base_servings <= 0:
        base_servings = 4
    if target_servings <= 0:
        target_servings = base_servings

    scale_factor = target_servings / base_servings

    scaled_ingredients = []
    for ing in ingredients:
        def replace_num(match):
            val = float(match.group(0))
            scaled_val = val * scale_factor
            return f"{scaled_val:.1f}".rstrip("0").rstrip(".")

        scaled_ing = re.sub(r"\d+(\.\d+)?", replace_num, ing)
        scaled_ingredients.append(scaled_ing)

    out = f"=== Recipe Portion Scaling ({base_servings} -> {target_servings} servings | {scale_factor:.2f}x) ===\n"
    out += "Scaled Ingredients:\n"
    for item in scaled_ingredients:
        out += f"- {item}\n"

    if calories_per_serving > 0:
        total_calories = calories_per_serving * target_servings
        out += f"\nEstimated Calories: {calories_per_serving} kcal/serving ({total_calories} kcal total for {target_servings} servings)"

    return out.strip()
