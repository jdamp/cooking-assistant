"""Cooking Agent - Multi-agent system for recipe and shopping list management."""

from cooking_agent.supervisor import create_supervisor_agent
from cooking_agent.bring import BringClient
from cooking_agent.mealie import MealieClient

__version__ = "0.1.0"

__all__ = [
    "create_supervisor_agent",
    "BringClient",
    "MealieClient",
]
