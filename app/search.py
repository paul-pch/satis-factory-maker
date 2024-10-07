#!/usr/bin/python3

import json
import typer

from rich.console import Console
from rich.table import Table
from rich.console import Console
from typing_extensions import Annotated

app = typer.Typer()
console = Console()


@app.command()
def item(query: Annotated[str, typer.Option()]):
    """
    Search for items in the data.
    """
    try:
        with open("data/data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        items = data.get("items", [])
        matching_items = [
            item for item in items if query.lower() in item["name"].lower()
        ]

        if matching_items:
            table = Table(title="Search Results")
            table.add_column("Name", justify="left", style="cyan")
            table.add_column("Key Name", justify="left", style="magenta")
            table.add_column("Tier", justify="right", style="green")
            table.add_column("Stack Size", justify="right", style="yellow")

            for item in matching_items:
                table.add_row(
                    item["name"],
                    item["key_name"],
                    str(item["tier"]),
                    str(item["stack_size"]),
                )

            console.print(table)
        else:
            console.print(f"[yellow]No items found matching '{query}'[/yellow]")
    except FileNotFoundError:
        console.print(
            "[red]Data file not found. Please fetch the data first using 'python satis.py fetch_data'.[/red]"
        )
    except json.JSONDecodeError:
        console.print("[red]Error decoding JSON data.[/red]")


@app.command()
def recipe(query: Annotated[str, typer.Option()]):
    """
    Search for recipes in the data.
    """
    try:
        with open("data/data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        recipes = data.get("recipes", [])
        matching_recipes = [
            recipe for recipe in recipes if query.lower() in recipe["name"].lower()
        ]

        if matching_recipes:
            table = Table(title="Search Results")
            table.add_column("Name", justify="left", style="cyan")
            table.add_column("Key Name", justify="left", style="magenta")
            table.add_column("Category", justify="left", style="green")
            table.add_column("Time", justify="right", style="yellow")
            table.add_column("Ingredients", justify="left", style="blue")
            table.add_column("Ingredients Rate", justify="right", style="blue")
            table.add_column("Products", justify="left", style="red")
            table.add_column("Products Rate", justify="right", style="red")

            for recipe in matching_recipes:
                ingredients = ", ".join(
                    f"{ingredient[0]} x{ingredient[1]}"
                    for ingredient in recipe["ingredients"]
                )
                products = ", ".join(
                    f"{product[0]} x{product[1]}" for product in recipe["products"]
                )
                ingredients_rate = ", ".join(
                    f"{ingredient[1]/recipe['time']*60:.2f}/min"
                    for ingredient in recipe["ingredients"]
                )
                products_rate = ", ".join(
                    f"{product[1]/recipe['time']*60:.2f}/min"
                    for product in recipe["products"]
                )
                table.add_row(
                    recipe["name"],
                    recipe["key_name"],
                    recipe["category"],
                    str(recipe["time"]),
                    ingredients,
                    ingredients_rate,
                    products,
                    products_rate,
                )

            console.print(table)
        else:
            console.print(f"[yellow]No recipes found matching '{query}'[/yellow]")
    except FileNotFoundError:
        console.print(
            "[red]Data file not found. Please fetch the data first using 'python satis.py fetch_data'.[/red]"
        )
    except json.JSONDecodeError:
        console.print("[red]Error decoding JSON data.[/red]")
