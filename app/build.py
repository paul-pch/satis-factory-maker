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
        resources = data.get("resources", [])
        fluids = data.get("fluids", [])

        # Check if the initial item queried exists in the items array based on the key_name
        item_exists = any(i["key_name"] == query for i in items)
        if not item_exists:
            console.print(f"[red]Item '{query}' not found.[/red]")
            raise typer.Exit(code=1)

        # Get the available recipe for item
        matching_recipes = get_recipes_for_item(recipes, query)
        display_recipes(matching_recipes, "Matching recipes")

        # Ask the user to choose a recipe
        recipe = choose_recipe(matching_recipes)
        display_recipes([recipe], "recette choisie")

        # Check if the recipe has any ingredients that are neither resources nor fluids
        complex_ingredients = check_ingredients(recipe, resources, fluids)
        if len(complex_ingredients) >= 1:
            console.print(
                f"[red]The following ingredients have to be build: {', '.join(complex_ingredients)}.[/red]"
            )
            return
        else:
            print("fin de build")

        # FIN

        # Voir pour sauvegarder le build final si c'est utile

    except FileNotFoundError:
        console.print(
            "[red]Data file not found. Please fetch the data first using 'python satis.py fetch_data'.[/red]"
        )
    except json.JSONDecodeError:
        console.print("[red]Error decoding JSON data.[/red]")


def choose_recipe(matching_recipes):
    console.print("Choose a recipe to use:")
    for i, recipe in enumerate(matching_recipes):
        console.print(f"[{i+1}] {recipe['key_name']}")
    choice = typer.prompt("Enter the number of the recipe you want to use")
    try:
        choice = int(choice)
        if choice < 1 or choice > len(matching_recipes):
            console.print("[red]Invalid choice.[/red]")
            raise typer.Exit(code=1)
        return matching_recipes[choice - 1]
    except ValueError:
        console.print("[red]Invalid choice.[/red]")
        raise typer.Exit(code=1)


def check_ingredients(recipe, resources, fluids):
    complex_ingredients = []
    for ingredient in recipe["ingredients"]:
        ingredient_key_name = ingredient[0]
        if not any(r["key_name"] == ingredient_key_name for r in resources) and not any(
            f["key_name"] == ingredient_key_name for f in fluids
        ):
            complex_ingredients.append(ingredient_key_name)
    return complex_ingredients


def get_recipes_for_item(recipes, query_item):
    # Get all the recipes that have the queried item in their products
    matching_recipes = [
        recipe
        for recipe in recipes
        if any(p[0] == query_item for p in recipe["products"])
    ]
    if not matching_recipes:
        console.print(f"[red]No recipe found for item '{query_item}'.[/red]")
        raise typer.Exit(code=1)

    return matching_recipes
