#!/usr/bin/python3

import math
from collections import defaultdict
from typing import Any, Literal

import typer
from rich.console import Console
from typing_extensions import Annotated

from app.models import ProductionLine, Recipe
from app.utils import display_factory, display_recipes, display_resources, load_data

app = typer.Typer()
console = Console(width=1000)
Json = dict[str, Any]

DATA = load_data("data/data.json")
ITEMS = DATA.get("items", [])
RECIPES = DATA.get("recipes", [])
RESOURCES = DATA.get("resources", [])
FLUIDS = DATA.get("fluids", [])


@app.callback(invoke_without_command=True)
def build(
    ctx: typer.Context,
    query: Annotated[str, typer.Option(help="Item to build")],
    minute_rate: Annotated[float, typer.Option(help="'Minute rate' wanted for the item")],
):
    """
    Build factory layer based on item name.
    """

    item_complex = get_item(query)

    factory: list[ProductionLine] = []

    plan(factory, item_complex, minute_rate, 0)

    factory = compact(factory)
    display_factory(factory)

    raw_resources = get_resources_rate(factory)
    display_resources(raw_resources)


def check_ingredients(recipe: Recipe) -> list[str]:
    complex_ingredients: list[str] = []
    for ingredient in recipe["ingredients"]:
        ingredient_key_name = ingredient[0]
        if not any(r["key_name"] == ingredient_key_name for r in RESOURCES) and not any(
            f["key_name"] == ingredient_key_name for f in FLUIDS
        ):
            complex_ingredients.append(ingredient_key_name)
    return complex_ingredients


def choose_recipe(matching_recipes: list[Recipe]) -> Recipe:
    console.print("Choose a recipe to use:")
    for i, recipe in enumerate(matching_recipes):
        console.print(f"[{i + 1}] {recipe['key_name']}")
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


def compact(factory: list[ProductionLine]) -> list[ProductionLine]:
    # Merge duplicate items production line
    grouped: defaultdict[str, list[ProductionLine]] = defaultdict(list)
    for line in factory:
        grouped[line.item].append(line)

    # Fusionner chaque groupe
    factory = [ProductionLine.merge(lines) for lines in grouped.values()]

    # Sort
    factory.sort(key=lambda x: x.layer)

    return factory


def get_item(query_item: str) -> dict[str, Any]:
    # Check if the item queried exists in the items array based on the key_name
    item_found = next((i for i in ITEMS if i["key_name"] == query_item), None)
    if not item_found:
        console.print(f"[red]Item '{query_item}' not found.[/red]")
        raise typer.Exit(code=1)
    return item_found


def get_minute_rate(recipe: Recipe, item: str, source: Literal["products", "ingredients"]) -> float:
    # Taux minute = (60 / (temps en secondes de production)) x Nombre produit de l'item en question pour cette recette
    return (60 / int(recipe["time"])) * int(next(p[1] for p in recipe[source] if p[0] == item))


def get_recipes_for_item(recipes: list[Recipe], query_item: str) -> list[Recipe]:
    # Get all the recipes that have the queried item in their products
    matching_recipes: list[Recipe] = [recipe for recipe in recipes if any(p[0] == query_item for p in recipe["products"])]
    if not matching_recipes:
        console.print(f"[red]No recipe found for item '{query_item}'.[/red]")
        raise typer.Exit(code=1)

    return matching_recipes


def get_resources_rate(factory: list[ProductionLine]) -> defaultdict[str, float]:
    raw_resources: defaultdict[str, float] = defaultdict(float)
    for line in factory:
        for resource in line.recipe["ingredients"]:
            if any(r["key_name"] == resource[0] for r in RESOURCES) or any(f["key_name"] == resource[0] for f in FLUIDS):
                raw_resources[resource[0]] += line.num_machine * get_minute_rate(line.recipe, resource[0], "ingredients")
    return raw_resources


def plan(factory: list[ProductionLine], item_complex: dict[str, Any], target_minute_rate: float, layer: int) -> None:
    # Get the available recipe for item
    matching_recipes = get_recipes_for_item(RECIPES, item_complex["key_name"])
    display_recipes(matching_recipes, "Matching recipes")

    # Ask the user to choose a recipe
    recipe = choose_recipe(matching_recipes)

    default_recipe_minute_rate = get_minute_rate(recipe, item_complex["key_name"], "products")
    num_machine: int = math.ceil(target_minute_rate / default_recipe_minute_rate)

    factory.append(
        ProductionLine(
            item=recipe["products"][0][0],
            building=recipe["category"],
            num_machine=num_machine,
            recipe=recipe,
            layer=layer,
        )
    )

    # Check if the recipe has any ingredients that are neither resources nor fluids
    complex_ingredients = check_ingredients(recipe)
    if len(complex_ingredients) >= 1:
        for ingredient in complex_ingredients:
            ingredient_minute_rate = get_minute_rate(recipe, ingredient, "ingredients")
            plan(
                factory,
                get_item(ingredient),
                ingredient_minute_rate * num_machine,
                layer + 1,
            )
