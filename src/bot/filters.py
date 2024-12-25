from telegram.ext import filters

def get_top_10_recipes(recipes, key):
    """Get top 10 recipes sorted by given key."""
    return sorted(recipes, key=lambda x: x[key], reverse=True)[:5]

recipe_filters = {
    "most_caloric": lambda recipes: get_top_10_recipes(recipes, 'calories'),
    "most_healthy": lambda recipes: get_top_10_recipes(recipes, 'healthScore'),
    "show_all": lambda recipes: recipes  # Show all found recipes
}
