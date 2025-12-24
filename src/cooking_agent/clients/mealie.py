"""Async Mealie API client."""

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class RecipeSummary:
    """Summary of a recipe from search results."""

    slug: str
    name: str
    description: str | None = None
    total_time: str | None = None
    image: str | None = None


@dataclass
class Ingredient:
    """Recipe ingredient."""

    note: str
    quantity: float | None = None
    unit: str | None = None
    food: str | None = None


@dataclass
class Recipe:
    """Full recipe details."""

    slug: str
    name: str
    description: str | None
    ingredients: list[Ingredient]
    instructions: list[str]
    total_time: str | None = None
    prep_time: str | None = None
    cook_time: str | None = None


class MealieClient:
    """Async client for Mealie REST API."""

    def __init__(self, base_url: str, api_token: str) -> None:
        """Initialize the Mealie client.

        Args:
            base_url: Mealie instance URL (e.g., http://localhost:9925)
            api_token: API token from Mealie user profile
        """
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "MealieClient":
        """Enter async context."""
        self._client = httpx.AsyncClient(
            base_url=f"{self.base_url}/api",
            headers={"Authorization": f"Bearer {self.api_token}"},
            timeout=30.0,
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context."""
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client, raising if not in context."""
        if self._client is None:
            raise RuntimeError("MealieClient must be used as async context manager")
        return self._client

    async def search_recipes(
        self,
        query: str | None = None,
        limit: int = 10,
    ) -> list[RecipeSummary]:
        """Search for recipes.

        Args:
            query: Search query string
            limit: Maximum number of results

        Returns:
            List of recipe summaries
        """
        params: dict[str, Any] = {"perPage": limit, "page": 1}
        if query:
            params["search"] = query

        response = await self.client.get("/recipes", params=params)
        response.raise_for_status()
        data = response.json()

        return [
            RecipeSummary(
                slug=item["slug"],
                name=item["name"],
                description=item.get("description"),
                total_time=item.get("totalTime"),
                image=item.get("image"),
            )
            for item in data.get("items", [])
        ]

    async def get_recipe(self, slug: str) -> Recipe:
        """Get full recipe details.

        Args:
            slug: Recipe slug/identifier

        Returns:
            Full recipe with ingredients and instructions
        """
        response = await self.client.get(f"/recipes/{slug}")
        response.raise_for_status()
        data = response.json()

        ingredients = [
            Ingredient(
                note=ing.get("note", ""),
                quantity=ing.get("quantity"),
                unit=ing.get("unit", {}).get("name") if ing.get("unit") else None,
                food=ing.get("food", {}).get("name") if ing.get("food") else None,
            )
            for ing in data.get("recipeIngredient", [])
        ]

        instructions = [
            step.get("text", "")
            for step in data.get("recipeInstructions", [])
        ]

        return Recipe(
            slug=data["slug"],
            name=data["name"],
            description=data.get("description"),
            ingredients=ingredients,
            instructions=instructions,
            total_time=data.get("totalTime"),
            prep_time=data.get("prepTime"),
            cook_time=data.get("cookTime"),
        )

    async def get_recipe_ingredients(self, slug: str) -> list[str]:
        """Get ingredient list for a recipe as strings.

        Args:
            slug: Recipe slug/identifier

        Returns:
            List of ingredient strings formatted for shopping list
        """
        recipe = await self.get_recipe(slug)
        result = []

        for ing in recipe.ingredients:
            parts = []
            if ing.quantity:
                parts.append(str(ing.quantity))
            if ing.unit:
                parts.append(ing.unit)
            if ing.food:
                parts.append(ing.food)
            elif ing.note:
                parts.append(ing.note)

            if parts:
                result.append(" ".join(parts))
            elif ing.note:
                result.append(ing.note)

        return result
