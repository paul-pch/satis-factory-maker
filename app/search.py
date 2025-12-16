#!/usr/bin/python3

import json
from typing import Optional

import typer
from rich.console import Console
from typing_extensions import Annotated

from app.utils import display_items, display_recipes, load_data

app = typer.Typer()
console = Console(width=1000)


@app.command()
def item(query: Annotated[str, typer.Option(help="Item to search")]):
    """
    Search for items in the data.
    """
    try:
        data = load_data("data/data.json")

        items = data.get("items", [])
        matching_items = [
            item for item in items if (query.lower() in item["name"].lower() or query.lower() in item["key_name"].lower())
        ]

        if matching_items:
            display_items(matching_items, "Search Results")
        else:
            console.print(f"[yellow]No items found matching '{query}'[/yellow]")

    except FileNotFoundError:
        console.print("[red]Data file not found. Please fetch the data first using 'python satis.py fetch_data'.[/red]")
    except json.JSONDecodeError:
        console.print("[red]Error decoding JSON data.[/red]")


@app.command()
def recipe(
    query: Annotated[str, typer.Option(help="Recipe to search")],
    output: Annotated[Optional[bool], typer.Option(help="Permet de ne filter les recettes avec 'query' en 'product'")] = False,
):
    """
    Search for recipes in the data.
    """
    try:
        data = load_data("data/data.json")

        recipes = data.get("recipes", [])
        matching_recipes = [
            recipe
            for recipe in recipes
            if (query.lower() in recipe["name"].lower() or query.lower() in recipe["key_name"].lower())
        ]

        if matching_recipes:
            # Filter the matching recipes based on query being present in "products"
            if output:
                filtered_recipes = [
                    recipe
                    for recipe in matching_recipes
                    if any(query.lower() in product[0].lower() for product in recipe["products"])
                ]
                matching_recipes = filtered_recipes

            display_recipes(matching_recipes, "Recipe Details")
        else:
            console.print(f"[yellow]No recipes found matching '{query}'[/yellow]")
    except FileNotFoundError:
        console.print("[red]Data file not found. Please fetch the data first using 'python satis.py fetch_data'.[/red]")
    except json.JSONDecodeError:
        console.print("[red]Error decoding JSON data.[/red]")
