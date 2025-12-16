import json
from typing import Any

from rich.console import Console
from rich.table import Table

from app.model import ProductionLine

Json = dict[str, Any]

console = Console(width=1000)


def load_data(file_path: str) -> Json:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        console.print("[red]Data file not found. Please fetch the data first using 'python satis.py fetch_data'.[/red]")
    except json.JSONDecodeError:
        console.print("[red]Error decoding JSON data.[/red]")
    return data


def display_items(items: list[dict[str, Any]], title: str) -> None:
    table = Table(title=title)
    table.add_column("Name", justify="left", style="cyan")
    table.add_column("Key Name", justify="left", style="magenta")
    table.add_column("Tier", justify="right", style="green")
    table.add_column("Stack Size", justify="right", style="yellow")

    for matching_item in items:
        table.add_row(
            matching_item["name"],
            matching_item["key_name"],
            str(matching_item["tier"]),
            str(matching_item.get("stack_size", "unknown")),
        )

    console.print(table)


def display_recipes(matching_recipes: list[dict[str, Any]], title: str) -> None:
    table = Table(title=title)
    table.add_column("Name", justify="left", style="cyan")
    table.add_column("Key Name", justify="left", style="magenta")
    table.add_column("Category", justify="left", style="green")
    table.add_column("Time", justify="right", style="yellow")
    table.add_column("Ingredients", justify="left", style="blue")
    table.add_column("Ingredients Rate", justify="right", style="blue")
    table.add_column("Products", justify="left", style="red")
    table.add_column("Products Rate", justify="right", style="red")

    for matching_recipe in matching_recipes:
        ingredients = ", ".join(
            f"{ingredient[0]} x{ingredient[1]}"
            for ingredient in matching_recipe["ingredients"]
        )
        products = ", ".join(
            f"{product[0]} x{product[1]}" for product in matching_recipe["products"]
        )
        ingredients_rate = ", ".join(
            f"{ingredient[1]/matching_recipe['time']*60:.2f}/min"
            for ingredient in matching_recipe["ingredients"]
        )
        products_rate = ", ".join(
            f"{product[1]/matching_recipe['time']*60:.2f}/min"
            for product in matching_recipe["products"]
        )
        table.add_row(
            matching_recipe["name"],
            matching_recipe["key_name"],
            matching_recipe["category"],
            str(matching_recipe["time"]),
            ingredients,
            ingredients_rate,
            products,
            products_rate,
        )

    console.print(table)

def display_factory(factory: list[ProductionLine], title: str = "Factory") -> None:
    table = Table(title=title)
    table.add_column("Layer", justify="left", style="cyan")
    table.add_column("Item", justify="left", style="cyan")
    table.add_column("Machine", justify="left", style="green")
    table.add_column("Nombre", justify="left", style="magenta")
    table.add_column("Entrée", justify="left", style="blue")
    table.add_column("Taux entrées", justify="right", style="red")
    table.add_column("Sorties", justify="left", style="blue")
    table.add_column("Taux sorties", justify="right", style="red")

    for prod_line in factory:
        ingredients = ", ".join(f"{ingredient[0]} x{ingredient[1]}" for ingredient in prod_line.inputs)
        products = ", ".join(f"{product[0]} x{product[1]}" for product in prod_line.outputs)
        ingredients_rate = ", ".join(f"{ingredient[1] / prod_line.time * 60:.2f}/min" for ingredient in prod_line.inputs)
        products_rate = ", ".join(f"{product[1] / prod_line.time * 60:.2f}/min" for product in prod_line.outputs)
        table.add_row(
            str(prod_line.layer),
            prod_line.item,
            prod_line.building,
            str(prod_line.num_machine),
            ingredients,
            ingredients_rate,
            products,
            products_rate,
        )

    console.print(table)
