"""Bring shopping list agent using LangGraph."""

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool


from cooking_agent.config import get_settings
from cooking_agent.bring.tools import (
    list_shopping_lists,
    view_shopping_list,
    add_to_shopping_list,
)


BRING_SYSTEM_PROMPT = """You are a shopping list assistant that helps users manage their Bring shopping lists.

Your capabilities:
- List available shopping lists
- View items on a specific shopping list
- Add items to shopping lists

When users want to manage shopping:
1. Use list_shopping_lists to show available lists
2. Use view_shopping_list to see current items
3. Use add_to_shopping_list to add new items

When adding items from a recipe, extract the key ingredient names (e.g., "chicken", "garlic", "olive oil") rather than full descriptions with quantities.

Be helpful and confirm actions you've taken."""


def create_bring_agent():
    bring_agent = create_agent(
        init_chat_model(model=get_settings().model_name, api_key=get_settings().openai_api_key),
        tools=[list_shopping_lists, view_shopping_list, add_to_shopping_list],
        system_prompt=BRING_SYSTEM_PROMPT,
    )
    return bring_agent


@tool
async def bring_shopping(query: str) -> str:
    """Interact with the Bring shopping list using natural language.
    
    Use this when the users wants to manage their shopping lists.

    Args:
        query: Natural language query about shopping lists (e.g Add "100g pasta" to "Grocery List")
    """
    bring_agent = create_bring_agent()
    
    result = await bring_agent.ainvoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].text
