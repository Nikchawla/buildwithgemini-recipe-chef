#!/usr/bin/env python3
"""Seed script for populating Firestore with recipe data."""

from google.cloud import firestore

# CRITICAL: Hardcode project ID as string for Firestore client.
# Do NOT use google.auth.default() or GOOGLE_CLOUD_PROJECT env var on Agent Platform.
PROJECT_ID = "qwiklabs-gcp-03-6c3aab0d52d4"

SEED_RECIPES = [
    {
        "id": "spaghetti-carbonara",
        "title": "Classic Spaghetti Carbonara",
        "cuisine": "Italian",
        "prep_time_mins": 10,
        "cook_time_mins": 15,
        "difficulty": "Easy",
        "ingredients": [
            "200g spaghetti",
            "100g pancetta or guanciale",
            "2 large eggs",
            "50g Pecorino Romano cheese",
            "Freshly ground black pepper",
            "Salt",
        ],
        "instructions": [
            "Boil pasta in salted water until al dente.",
            "Sauté pancetta in a skillet until crispy.",
            "Beat eggs and mix with grated Pecorino Romano.",
            "Drain pasta, reserving a little pasta water.",
            "Combine pasta, pancetta, and egg-cheese mixture off heat, tossing quickly to create a creamy sauce.",
        ],
        "calories_per_serving": 610,
        "dietary_tags": ["nut-free"],
    },
    {
        "id": "avocado-toast-poached-egg",
        "title": "Avocado Toast with Poached Egg",
        "cuisine": "American",
        "prep_time_mins": 10,
        "cook_time_mins": 5,
        "difficulty": "Easy",
        "ingredients": [
            "2 slices sourdough bread",
            "1 ripe avocado",
            "2 eggs",
            "1 tsp lemon juice",
            "Red pepper flakes",
            "Salt and pepper",
        ],
        "instructions": [
            "Toast sourdough slices until golden.",
            "Mash avocado with lemon juice, salt, and pepper.",
            "Poach eggs in simmering water with vinegar for 3 minutes.",
            "Spread avocado on toast, top with poached eggs, and sprinkle red pepper flakes.",
        ],
        "calories_per_serving": 380,
        "dietary_tags": ["vegetarian", "dairy-free", "nut-free"],
    },
    {
        "id": "thai-green-curry-tofu",
        "title": "Thai Green Curry with Tofu & Vegetables",
        "cuisine": "Thai",
        "prep_time_mins": 15,
        "cook_time_mins": 20,
        "difficulty": "Medium",
        "ingredients": [
            "200g firm tofu (cubed)",
            "2 tbsp green curry paste",
            "400ml coconut milk",
            "1 bell pepper (sliced)",
            "100g snap peas",
            "1 tbsp soy sauce",
            "Fresh basil leaves",
        ],
        "instructions": [
            "Pan-fry tofu cubes until golden and set aside.",
            "Sauté green curry paste in a pot for 1 minute.",
            "Add coconut milk and bring to a gentle simmer.",
            "Add bell pepper, snap peas, and tofu; cook for 8-10 minutes.",
            "Stir in soy sauce and fresh basil. Serve hot.",
        ],
        "calories_per_serving": 450,
        "dietary_tags": ["vegan", "vegetarian", "dairy-free", "gluten-free"],
    },
    {
        "id": "chicken-tikka-masala",
        "title": "Creamy Chicken Tikka Masala",
        "cuisine": "Indian",
        "prep_time_mins": 20,
        "cook_time_mins": 30,
        "difficulty": "Medium",
        "ingredients": [
            "500g boneless chicken thighs",
            "1/2 cup yogurt",
            "2 tbsp tikka masala spices",
            "1 onion (finely chopped)",
            "2 cloves garlic (minced)",
            "1 tbsp ginger (grated)",
            "400g canned crushed tomatoes",
            "1/2 cup heavy cream",
            "Fresh cilantro",
        ],
        "instructions": [
            "Marinate chicken in yogurt and spices for 15 minutes.",
            "Sear chicken pieces in a skillet until browned; remove and set aside.",
            "Sauté onion, garlic, and ginger until fragrant.",
            "Add crushed tomatoes and simmer for 10 minutes.",
            "Stir in heavy cream and return chicken to pan; simmer until cooked.",
        ],
        "calories_per_serving": 520,
        "dietary_tags": ["gluten-free", "nut-free"],
    },
]


def seed_database():
    db = firestore.Client(project=PROJECT_ID)
    recipes_ref = db.collection("recipes")

    print(f"Seeding Firestore collection 'recipes' in project '{PROJECT_ID}'...")
    for recipe in SEED_RECIPES:
        doc_id = recipe["id"]
        recipes_ref.document(doc_id).set(recipe)
        print(f"  ✓ Added recipe: {recipe['title']} (ID: {doc_id})")

    print("✅ Firestore seeding completed successfully!")


if __name__ == "__main__":
    seed_database()
