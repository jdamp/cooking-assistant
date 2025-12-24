"""Async Bring shopping list client wrapper."""

from dataclasses import dataclass
from typing import Any

import aiohttp
from bring_api import Bring, BringItemOperation


@dataclass
class ShoppingList:
    """Shopping list info."""

    uuid: str
    name: str


@dataclass
class ShoppingItem:
    """Item on a shopping list."""

    name: str
    specification: str | None = None


class BringClient:
    """Async wrapper around the bring-api library."""

    def __init__(self, email: str, password: str) -> None:
        """Initialize the Bring client.

        Args:
            email: Bring account email
            password: Bring account password
        """
        self.email = email
        self.password = password
        self._session: aiohttp.ClientSession | None = None
        self._bring: Bring | None = None

    async def __aenter__(self) -> "BringClient":
        """Enter async context and login."""
        self._session = aiohttp.ClientSession()
        self._bring = Bring(self._session, self.email, self.password)
        await self._bring.login()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context."""
        if self._session:
            await self._session.close()

    @property
    def bring(self) -> Bring:
        """Get the Bring instance, raising if not in context."""
        if self._bring is None:
            raise RuntimeError("BringClient must be used as async context manager")
        return self._bring

    async def get_shopping_lists(self) -> list[ShoppingList]:
        """Get all available shopping lists.

        Returns:
            List of shopping lists
        """
        result = await self.bring.load_lists()
        return [
            ShoppingList(uuid=lst.listUuid, name=lst.name)
            for lst in result.lists
        ]

    async def get_list_items(self, list_uuid: str) -> list[ShoppingItem]:
        """Get items from a shopping list.

        Args:
            list_uuid: UUID of the shopping list

        Returns:
            List of items currently on the list
        """
        result = await self.bring.get_list(list_uuid)
        return [
            ShoppingItem(
                name=item.itemId,
                specification=item.specification or None,
            )
            for item in result.items.purchase
        ]

    async def add_items(
        self,
        list_uuid: str,
        items: list[str | tuple[str, str]],
    ) -> None:
        """Add items to a shopping list.

        Args:
            list_uuid: UUID of the shopping list
            items: List of item names, or tuples of (name, specification)
        """
        batch_items = []
        for item in items:
            if isinstance(item, tuple):
                name, spec = item
                batch_items.append({"itemId": name, "spec": spec})
            else:
                batch_items.append({"itemId": item})

        if batch_items:
            await self.bring.batch_update_list(
                list_uuid,
                batch_items,
                BringItemOperation.ADD,
            )

    async def remove_item(self, list_uuid: str, item_name: str) -> None:
        """Remove an item from a shopping list.

        Args:
            list_uuid: UUID of the shopping list
            item_name: Name of item to remove
        """
        await self.bring.batch_update_list(
            list_uuid,
            {"itemId": item_name},
            BringItemOperation.REMOVE,
        )

    async def complete_item(self, list_uuid: str, item_name: str) -> None:
        """Mark an item as complete/bought.

        Args:
            list_uuid: UUID of the shopping list
            item_name: Name of item to complete
        """
        await self.bring.batch_update_list(
            list_uuid,
            {"itemId": item_name},
            BringItemOperation.COMPLETE,
        )

    async def get_list_by_name(self, name: str) -> ShoppingList | None:
        """Find a shopping list by name.

        Args:
            name: Name of the shopping list

        Returns:
            ShoppingList if found, None otherwise
        """
        lists = await self.get_shopping_lists()
        for lst in lists:
            if lst.name.lower() == name.lower():
                return lst
        return None
