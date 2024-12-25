import requests
import logging
from config.config import SPOONACULAR_API_KEY
from src.services.translator import translate_to_russian, clean_and_translate_instructions, clean_and_translate_summary

logger = logging.getLogger(__name__)

def get_recipes(ingredients, number=2, ranking=1):
    try:
        base_recipes = _get_base_recipes(ingredients, number, ranking)
        logger.info(f"Base recipes found: {len(base_recipes)}")
        detailed_recipes = _enrich_recipes_with_details(base_recipes)
        logger.info(f"Detailed recipes processed: {len(detailed_recipes)}")
        return detailed_recipes
    except Exception as e:
        logger.info(f"Error fetching recipes: {e}")
        return []

def _get_base_recipes(ingredients, number, ranking):
    ingredients_str = ",".join([ingredient.strip() for ingredient in ingredients])
    url = f"https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "ingredients": ingredients_str,
        "number": number,
        "apiKey": SPOONACULAR_API_KEY,
        "ranking": ranking,
        "ignorePantry": False,
        "limitLicense": True
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def _enrich_recipes_with_details(base_recipes):
    detailed_recipes = []
    for recipe in base_recipes:
        details = _get_recipe_details(recipe['id'])
        
        # Get instructions from either regular instructions or analyzedInstructions
        instructions = details.get('instructions')
        if not instructions:
            analyzed = details.get('analyzedInstructions', [])
            if analyzed:
                steps = analyzed[0].get('steps', [])
                instructions = "\n".join([f"Шаг {i+1}: {step['step']}" for i, step in enumerate(steps)])
        
        translated_instructions = clean_and_translate_instructions(instructions)
        
        detailed_recipes.append({
            "title": translate_to_russian(recipe.get("title")),
            "id": recipe.get("id"),
            "url": details.get("spoonacularSourceUrl"),
            "image": recipe.get("image"),
            "calories": _extract_calories(details),
            "healthScore": details.get('healthScore', 0),
            "summary": clean_and_translate_summary(details.get('summary')),
            "instructions": translated_instructions,
            "pricePerServing": details.get('pricePerServing', 0),
            "extendedIngredients": details.get('extendedIngredients', [])
        })
    
    return detailed_recipes


def _get_recipe_details(recipe_id):
    """Fetch detailed information for a specific recipe."""
    details_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    details_params = {
        "apiKey": SPOONACULAR_API_KEY,
        "includeNutrition": True
    }
    response = requests.get(details_url, params=details_params)
    details = response.json()
    
    # logger.info(f"Recipe {recipe_id} instructions present: {bool(details.get('instructions'))}")
    # logger.info(f"Raw instructions data: {details.get('instructions')}")
    
    return details

def _extract_calories(details):
    """Extract calorie information from recipe details."""
    return next((nutrient['amount'] 
                for nutrient in details.get('nutrition', {}).get('nutrients', []) 
                if nutrient['name'] == 'Calories'), 0)
