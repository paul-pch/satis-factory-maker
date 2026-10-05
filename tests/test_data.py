"""Consistency checks on the committed data/data.json."""

import pytest

from app.utils import load_data

DATA = load_data("data/data.json")
KNOWN = {e["key_name"] for e in DATA["items"] + DATA["fluids"]}


@pytest.mark.parametrize("section", ["belts", "pipes", "buildings", "miners", "items", "fluids", "recipes", "resources"])
def test_sections_are_present_with_unique_keys(section):
    keys = [e["key_name"] for e in DATA[section]]
    assert keys
    assert len(keys) == len(set(keys))


def test_recipes_reference_known_items_and_buildings():
    categories = {b["category"] for b in DATA["buildings"]}
    for recipe in DATA["recipes"]:
        assert recipe["category"] in categories, recipe["key_name"]
        assert recipe["time"] > 0, recipe["key_name"]
        assert recipe["products"], recipe["key_name"]
        for key_name, amount in recipe["ingredients"] + recipe["products"]:
            assert key_name in KNOWN, (recipe["key_name"], key_name)
            assert amount > 0, (recipe["key_name"], key_name)


def test_resources_are_known_items_or_fluids():
    assert {r["key_name"] for r in DATA["resources"]} <= KNOWN
