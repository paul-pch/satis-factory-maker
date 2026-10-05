from typing import Any

import pytest

import app.build
import app.search

Json = dict[str, Any]


@pytest.fixture
def data() -> Json:
    """Small data set in the data/data.json format."""
    return {
        "items": [
            {"name": "Iron Ore", "key_name": "iron-ore", "tier": -1, "stack_size": 100},
            {"name": "Iron Ingot", "key_name": "iron-ingot", "tier": 0, "stack_size": 100},
            {"name": "Iron Plate", "key_name": "iron-plate", "tier": 0, "stack_size": 200},
            {"name": "Iron Rod", "key_name": "iron-rod", "tier": 0, "stack_size": 200},
            {"name": "Screws", "key_name": "screws", "tier": 0, "stack_size": 500},
            {"name": "Reinforced Iron Plate", "key_name": "reinforced-iron-plate", "tier": 0, "stack_size": 100},
            {"name": "Mystery Part", "key_name": "mystery-part", "tier": None, "stack_size": None},
        ],
        "fluids": [
            {"name": "Water", "key_name": "water", "tier": -1},
        ],
        "resources": [
            {"key_name": "iron-ore", "category": "mineral"},
            {"key_name": "water", "category": "fluid"},
        ],
        "recipes": [
            {
                "name": "Iron Ingot",
                "key_name": "iron-ingot",
                "category": "smelting1",
                "time": 2,
                "ingredients": [["iron-ore", 1]],
                "products": [["iron-ingot", 1]],
            },
            {
                "name": "Iron Plate",
                "key_name": "iron-plate",
                "category": "crafting1",
                "time": 6,
                "ingredients": [["iron-ingot", 3]],
                "products": [["iron-plate", 2]],
            },
            {
                "name": "Iron Rod",
                "key_name": "iron-rod",
                "category": "crafting1",
                "time": 4,
                "ingredients": [["iron-ingot", 1]],
                "products": [["iron-rod", 1]],
            },
            {
                "name": "Screws",
                "key_name": "screws",
                "category": "crafting1",
                "time": 6,
                "ingredients": [["iron-rod", 1]],
                "products": [["screws", 4]],
            },
            {
                "name": "Reinforced Iron Plate",
                "key_name": "reinforced-iron-plate",
                "category": "crafting2",
                "time": 12,
                "ingredients": [["iron-plate", 6], ["screws", 12]],
                "products": [["reinforced-iron-plate", 1]],
            },
            {
                "name": "Alternate: Iron Wire Plate",
                "key_name": "alt-iron-wire-plate",
                "category": "crafting1",
                "time": 6,
                "ingredients": [["iron-ingot", 6], ["water", 3]],
                "products": [["iron-plate", 4]],
            },
        ],
    }


@pytest.fixture
def patched_data(data: Json, monkeypatch: pytest.MonkeyPatch) -> Json:
    """Replace the data loaded at import time by search and build with the small data set."""
    for module in (app.search, app.build):
        monkeypatch.setattr(module, "ITEMS", data["items"])
        monkeypatch.setattr(module, "RECIPES", data["recipes"])
        monkeypatch.setattr(module, "RESOURCES", data["resources"])
        monkeypatch.setattr(module, "FLUIDS", data["fluids"])
    return data
