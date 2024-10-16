#!/usr/bin/python3

import json
import typer

from rich.console import Console
from typing_extensions import Annotated
from .utils import load_data


app = typer.Typer()
console = Console(width=1000)


@app.command()
def item(query: Annotated[str, typer.Option(help="Item to build")]):
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

        # Check if the item queried has an existing recipe in the recipes array
        recipe_exists = any(any(p[0] == query for p in r["products"]) for r in recipes)
        if not recipe_exists:
            console.print(f"[red]No recipe found for item '{query}'.[/red]")
            return

        ## TODO
        ## Je veux afficher la recette à cette étape
        ## Mais je dois d'abord factoriser une fonction d'affichage de recette

    except FileNotFoundError:
        console.print(
            "[red]Data file not found. Please fetch the data first using 'python satis.py fetch_data'.[/red]"
        )
    except json.JSONDecodeError:
        console.print("[red]Error decoding JSON data.[/red]")
