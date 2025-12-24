#!/usr/bin/python3


import typer
from rich.console import Console
from typing_extensions import Annotated

from app.utils import display_items, display_recipes, load_data

app = typer.Typer()
console = Console(width=1000)

DATA = load_data("data/data.json")
ITEMS = DATA.get("items", [])
RECIPES = DATA.get("recipes", [])
RESOURCES = DATA.get("resources", [])
FLUIDS = DATA.get("fluids", [])


@app.command()
def item(query: Annotated[str, typer.Option(help="Item to search")]):
    """
    Search for items in the data.
    """
    query = query.lower()
    matching_items = [item for item in ITEMS if (query in item["name"].lower() or query in item["key_name"].lower())]

    if matching_items:
        display_items(matching_items, "Search Results")
    else:
        console.print(f"[yellow]No items found matching '{query}'[/yellow]")


@app.command()
def recipe(
    query: Annotated[str, typer.Option(help="Recipe to search")],
):
    """
    Search for recipes in the data.
    """
    query = query.lower()

    matching_recipes = [
        recipe
        for recipe in RECIPES
        if (query in recipe["name"].lower() or query in recipe["key_name"].lower())
        or any(query.lower() in product[0].lower() for product in recipe["products"])
    ]

    if matching_recipes:
        display_recipes(matching_recipes, "Recipe Details")
    else:
        console.print(f"[yellow]No recipes found matching '{query}'[/yellow]")
