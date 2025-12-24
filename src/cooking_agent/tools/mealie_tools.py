"""LangChain tools for Mealie recipe management."""

from langchain_core.tools import tool

from cooking_agent.clients.mealie import MealieClient
from cooking_agent.config import get_settings


def _get_mealie_client() -> MealieClient:
    """Get a configured Mealie client."""
    settings = get_settings()
    return MealieClient(settings.mealie_url, settings.mealie_api_token)


@tool
async def search_recipes(query: str, limit: int = 5) -> str:
    """Search for recipes by name or ingredients.

    Args:
        query: Search query (recipe name, ingredient, or keyword)
        limit: Maximum number of results to return (default: 5)

    Returns:
        Formatted list of matching recipes with their slugs
    """
    async with _get_mealie_client() as client:
        recipes = await client.search_recipes(query, limit=limit)

    if not recipes:
        return f"No recipes found matching '{query}'"

    lines = [f"Found {len(recipes)} recipes:"]
    for r in recipes:
        desc = f" - {r.description[:50]}..." if r.description else ""
        time_info = f" ({r.total_time})" if r.total_time else ""
        lines.append(f"• {r.name}{time_info}{desc}")
        lines.append(f"  slug: {r.slug}")

    return "\n".join(lines)


@tool
async def get_recipe_details(recipe_slug: str) -> str:
    """Get full recipe details including instructions.

    Args:
        recipe_slug: The slug identifier of the recipe (from search results)

    Returns:
        Full recipe with ingredients and cooking instructions
    """
    async with _get_mealie_client() as client:
        recipe = await client.get_recipe(recipe_slug)

    lines = [f"# {recipe.name}"]

    if recipe.description:
        lines.append(f"\n{recipe.description}")

    times = []
    if recipe.prep_time:
        times.append(f"Prep: {recipe.prep_time}")
    if recipe.cook_time:
        times.append(f"Cook: {recipe.cook_time}")
    if recipe.total_time:
        times.append(f"Total: {recipe.total_time}")
    if times:
        lines.append(f"\n⏱️ {' | '.join(times)}")

    lines.append("\n## Ingredients")
    for ing in recipe.ingredients:
        parts = []
        if ing.quantity:
            parts.append(str(ing.quantity))
        if ing.unit:
            parts.append(ing.unit)
        if ing.food:
            parts.append(ing.food)
        if ing.note and ing.food:
            parts.append(f"({ing.note})")
        elif ing.note:
            parts.append(ing.note)
        lines.append(f"• {' '.join(parts)}")

    lines.append("\n## Instructions")
    for i, step in enumerate(recipe.instructions, 1):
        lines.append(f"{i}. {step}")

    return "\n".join(lines)


@tool
async def get_recipe_ingredients(recipe_slug: str) -> str:
    """Get the ingredient list for a recipe.

    Use this to get ingredients that can be added to a shopping list.

    Args:
        recipe_slug: The slug identifier of the recipe

    Returns:
        List of ingredients formatted for shopping
    """
    async with _get_mealie_client() as client:
        recipe = await client.get_recipe(recipe_slug)
        ingredients = await client.get_recipe_ingredients(recipe_slug)

    lines = [f"Ingredients for {recipe.name}:"]
    for ing in ingredients:
        lines.append(f"• {ing}")

    return "\n".join(lines)
