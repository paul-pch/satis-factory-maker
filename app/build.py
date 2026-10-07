#!/usr/bin/python3

import math
from collections import defaultdict
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Annotated, Any, Literal, NoReturn

import typer
from rich.console import Console

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

ID_DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"


@dataclass
class RecipeChoices:
    """Recipe choices of a build: asked to the user or replayed from a factory ID.

    In simple mode (default), the first choice made for an item is reused for every other occurrence of that item.
    In complex mode, a choice is made for every node of the tree.
    """

    complex: bool = False
    preset: Iterator[int] | None = None
    made: list[int] = field(default_factory=list)
    by_item: dict[str, int] = field(default_factory=dict)

    def choose(self, item: str, matching_recipes: list[Recipe], minute_rate: float) -> int:
        if not self.complex and item in self.by_item:
            return self.by_item[item]

        if self.preset is not None:
            choice = next(self.preset, None)
            if choice is None or choice > len(matching_recipes):
                invalid_factory_id()
        else:
            display_recipes(matching_recipes, f"Matching recipes · [bold]{item}[/bold] · {minute_rate:.2f}/min", numbered=True)
            choice = choose_recipe(matching_recipes)

        self.made.append(choice)
        self.by_item.setdefault(item, choice)
        return choice


@app.callback(invoke_without_command=True)
def build(
    ctx: typer.Context,
    minute_rate: Annotated[float, typer.Option(help="'Minute rate' wanted for the item")],
    query: Annotated[str | None, typer.Option(help="Item to build")] = None,
    factory_id: Annotated[
        str | None, typer.Option("--id", help="Factory ID printed by a previous build: replays its recipe choices")
    ] = None,
    complex_mode: Annotated[
        bool, typer.Option("--complex", help="Choose a recipe for every node of the tree, even for items already chosen")
    ] = False,
):
    """
    Build factory layer based on item name.
    """

    choices = RecipeChoices(complex=complex_mode)
    if factory_id is not None:
        query, choices = decode_factory_id(factory_id, query, complex_mode)
    elif query is None:
        console.print("[red]Missing option '--query' (or '--id').[/red]")
        raise typer.Exit(code=1)

    item_complex = get_item(query)

    factory: list[ProductionLine] = []
    imports: defaultdict[str, float] = defaultdict(float)

    plan(factory, imports, item_complex, minute_rate, 0, choices)

    if choices.preset is not None and next(choices.preset, None) is not None:
        invalid_factory_id()

    factory = compact(factory)
    display_factory(factory, f"Factory · [bold]{query}[/bold] · {minute_rate:.2f}/min")

    raw_resources = get_resources_rate(factory)
    display_resources(raw_resources)

    if imports:
        display_resources(imports, "Imports en gare")

    console.print(f"ID usine : [bold]{encode_factory_id(query, choices)}[/bold]")


def check_ingredients(recipe: Recipe) -> list[str]:
    complex_ingredients: list[str] = []
    for ingredient in recipe["ingredients"]:
        ingredient_key_name = ingredient[0]
        if not any(r["key_name"] == ingredient_key_name for r in RESOURCES) and not any(
            f["key_name"] == ingredient_key_name for f in FLUIDS
        ):
            complex_ingredients.append(ingredient_key_name)
    return complex_ingredients


def choose_recipe(matching_recipes: list[Recipe]) -> int:
    """Return the chosen recipe number: 1-based index in matching_recipes, 0 when the item is imported."""
    console.print("Choose a recipe to use:")
    console.print("[0] import (unlimited supply from a train station)")
    for i, recipe in enumerate(matching_recipes):
        console.print(f"[{i + 1}] {recipe['key_name']}")
    choice = typer.prompt("Enter the number of the recipe you want to use")
    try:
        choice = int(choice)
        if choice < 0 or choice > len(matching_recipes):
            console.print("[red]Invalid choice.[/red]")
            raise typer.Exit(code=1)
        return choice
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


def decode_factory_id(factory_id: str, query: str | None, complex_mode: bool) -> tuple[str, RecipeChoices]:
    """Split a factory ID into the target item and its recipe choices, in plan() order.

    `item:choices` is a simple mode ID, `item::choices` a complex mode one.
    """
    item, separator, digits = factory_id.partition(":")
    id_complex = digits.startswith(":")
    digits = digits.removeprefix(":")
    if not item or not separator or any(d not in ID_DIGITS for d in digits):
        invalid_factory_id()
    if query is not None and query != item:
        console.print(f"[red]Factory ID builds '{item}', not '{query}'.[/red]")
        raise typer.Exit(code=1)
    if complex_mode and not id_complex:
        console.print("[red]--complex given with a simple mode factory ID.[/red]")
        raise typer.Exit(code=1)
    return item, RecipeChoices(complex=id_complex, preset=iter([ID_DIGITS.index(d) for d in digits]))


def encode_factory_id(item: str, choices: RecipeChoices) -> str:
    separator = "::" if choices.complex else ":"
    return f"{item}{separator}{''.join(ID_DIGITS[c] for c in choices.made)}"


def invalid_factory_id() -> NoReturn:
    console.print("[red]Invalid factory ID (or game data changed since it was generated).[/red]")
    raise typer.Exit(code=1)


def get_item(query_item: str) -> dict[str, Any]:
    # Check if the item queried exists in the items array based on the key_name
    item_found = next((i for i in ITEMS if i["key_name"] == query_item), None)
    if not item_found:
        console.print(f"[red]Item '{query_item}' not found.[/red]")
        raise typer.Exit(code=1)
    return item_found


def get_minute_rate(recipe: Recipe, item: str, source: Literal["products", "ingredients"]) -> float:
    # Taux minute = (60 / (temps en secondes de production)) x Nombre produit de l'item en question pour cette recette
    return (60 / float(recipe["time"])) * float(next(p[1] for p in recipe[source] if p[0] == item))


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


def plan(
    factory: list[ProductionLine],
    imports: defaultdict[str, float],
    item_complex: dict[str, Any],
    target_minute_rate: float,
    layer: int,
    choices: RecipeChoices,
) -> None:
    # Get the available recipe for item
    matching_recipes = get_recipes_for_item(RECIPES, item_complex["key_name"])

    # Ask the user to choose a recipe (or reuse / replay a choice)
    choice = choices.choose(item_complex["key_name"], matching_recipes, target_minute_rate)

    if choice == 0:
        imports[item_complex["key_name"]] += target_minute_rate
        return
    recipe = matching_recipes[choice - 1]

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
                imports,
                get_item(ingredient),
                ingredient_minute_rate * num_machine,
                layer + 1,
                choices,
            )
