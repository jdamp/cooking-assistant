"""LangChain tools for Bring shopping list management."""

from langchain_core.tools import tool

from cooking_agent.bring.client import BringClient
from cooking_agent.config import get_settings


def _get_bring_client() -> BringClient:
    """Get a configured Bring client."""
    settings = get_settings()
    return BringClient(settings.bring_email, settings.bring_password)


@tool
async def list_shopping_lists() -> str:
    """List all available shopping lists.

    Returns:
        List of shopping list names and their UUIDs
    """
    async with _get_bring_client() as client:
        lists = await client.get_shopping_lists()

    if not lists:
        return "No shopping lists found"

    lines = ["Your shopping lists:"]
    for lst in lists:
        lines.append(f"• {lst.name} (uuid: {lst.uuid})")

    return "\n".join(lines)


@tool
async def view_shopping_list(list_name: str) -> str:
    """View items currently on a shopping list.

    Args:
        list_name: Name of the shopping list to view

    Returns:
        List of items on the shopping list
    """
    async with _get_bring_client() as client:
        lst = await client.get_list_by_name(list_name)
        if not lst:
            lists = await client.get_shopping_lists()
            available = ", ".join(l.name for l in lists)
            return f"Shopping list '{list_name}' not found. Available lists: {available}"

        items = await client.get_list_items(lst.uuid)

    if not items:
        return f"Shopping list '{list_name}' is empty"

    lines = [f"Items on '{list_name}':"]
    for item in items:
        spec = f" ({item.specification})" if item.specification else ""
        lines.append(f"• {item.name}{spec}")

    return "\n".join(lines)


@tool
async def add_to_shopping_list(list_name: str, items: list[str]) -> str:
    """Add items to a shopping list.

    Args:
        list_name: Name of the shopping list
        items: List of item names to add

    Returns:
        Confirmation of items added
    """
    async with _get_bring_client() as client:
        lst = await client.get_list_by_name(list_name)
        if not lst:
            lists = await client.get_shopping_lists()
            available = ", ".join(l.name for l in lists)
            return f"Shopping list '{list_name}' not found. Available lists: {available}"

        await client.add_items(lst.uuid, items)

    return f"Added {len(items)} items to '{list_name}': {', '.join(items)}"
