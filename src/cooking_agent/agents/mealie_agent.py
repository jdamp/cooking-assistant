"""Mealie recipe agent using LangGraph."""

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool

from cooking_agent.config import get_settings
from cooking_agent.tools.mealie_tools import (
    search_recipes,
    get_recipe_details,
    get_recipe_ingredients,
)


MEALIE_SYSTEM_PROMPT = """You are a recipe management assistant that helps users find and explore recipes from their Mealie collection.

Your capabilities:
- Search for recipes by name, ingredients, or keywords
- Get full recipe details including ingredients and instructions
- Extract ingredient lists for shopping

When users ask about recipes:
1. Use search_recipes to find matching recipes
2. Use get_recipe_details to show full recipe information
3. Use get_recipe_ingredients when users want ingredients for shopping

Always provide helpful, concise responses about the recipes you find.

Recipes might be in English or German.
"""


def create_mealie_agent():
    mealie_agent = create_agent(
        init_chat_model(model=get_settings().model_name, api_key=get_settings().openai_api_key),
        tools=[search_recipes, get_recipe_details, get_recipe_ingredients],
        system_prompt=MEALIE_SYSTEM_PROMPT,
    )
    return mealie_agent


@tool
async def mealie_recipes(query: str) -> str:
    """Interact with Mealie recipes using natural language.
    
    Use this when the users wants to search for recipes, get recipe details, or extract ingredient lists.

    Args:
        query: Natural language query about recipes (e.g "Retrieve the ingrendients for the "Nudeln mit Kartoffeln" recipe)
    """
    mealie_agent = create_mealie_agent()
    
    result = await mealie_agent.ainvoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].text