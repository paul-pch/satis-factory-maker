#!/usr/bin/python3

import json
import typer

from rich.console import Console
from typing_extensions import Annotated
from .utils import load_data, display_recipes


app = typer.Typer()
console = Console(width=1000)


@app.command()
def item(
    query: Annotated[str, typer.Option(help="Item to build")],
    minute_rate: Annotated[
        float, typer.Option(help="'Minute rate' wanted for the item")
    ],
):
    """
    Build factory layer based on item name.
    """
    try:
        data = load_data("data/data.json")
        items = data.get("items", [])
        recipes = data.get("recipes", [])

        # Check if the item queried exists in the items array based on the key_name
        item_exists = any(i["key_name"] == query for i in items)
        if not item_exists:
            console.print(f"[red]Item '{query}' not found.[/red]")
            return

        # Get all the recipes that have the queried item in their products
        matching_recipes = [
            recipe
            for recipe in recipes
            if any(p[0] == query for p in recipe["products"])
        ]
        if not matching_recipes:
            console.print(f"[red]No recipe found for item '{query}'.[/red]")
            return

        display_recipes(matching_recipes, "Matching recipes")

        ## TOOD
        ## Maintenant faut demander à choisir la recette qu'on veut

    except FileNotFoundError:
        console.print(
            "[red]Data file not found. Please fetch the data first using 'python satis.py fetch_data'.[/red]"
        )
    except json.JSONDecodeError:
        console.print("[red]Error decoding JSON data.[/red]")
