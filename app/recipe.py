from typing import Optional

import typer

from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated
from .utils import load_data, save_data

app = typer.Typer()


@app.command()
def create(
    name: Annotated[str, typer.Option(prompt="Nom de la recette")],
    machine: Annotated[str, typer.Option(prompt="Machine")],
):
    input_items = {}
    output_items = {}

    items = load_data("items.json")
    item_names = [item["name"] for item in items]

    while True:
        item = typer.prompt("Nom de l'item d'entrée (ou 'done' pour terminer)")
        if item.lower() == "done":
            break
        if item not in item_names:
            typer.echo(f"L'item '{item}' n'existe pas. Veuillez réessayer.")
            continue
        rate = float(typer.prompt(f"Taux de {item} par minute"))
        input_items[item] = rate

    while True:
        item = typer.prompt("Nom de l'item de sortie (ou 'done' pour terminer)")
        if item.lower() == "done":
            break
        if item not in item_names:
            typer.echo(f"L'item '{item}' n'existe pas. Veuillez réessayer.")
            continue
        rate = float(typer.prompt(f"Taux de {item} par minute"))
        output_items[item] = rate

    if not input_items or not output_items:
        typer.echo(
            "Une recette doit avoir au moins un item d'entrée et un item de sortie."
        )
        raise typer.Exit(code=1)

    recipe = {
        "name": name,
        "machine": machine,
        "input": input_items,
        "output": output_items,
    }

    recipes = load_data("recipes.json")
    recipes.append(recipe)
    save_data("recipes.json", recipes)
    typer.echo("Recette ajoutée avec succès!")


@app.command()
def edit(
    name: Annotated[str, typer.Option(prompt="Nom de la recette à modifier")],
    machine: Annotated[
        Optional[str],
        typer.Option(prompt="Nouvelle machine (laisser vide pour ne pas modifier)"),
    ],
):
    recipes = load_data("recipes.json")
    recipe = next((r for r in recipes if r["name"] == name), None)
    if recipe is None:
        typer.echo(f"La recette '{name}' n'existe pas.")
        raise typer.Exit(code=1)

    if machine:
        recipe["machine"] = machine

    items = load_data("items.json")
    item_names = [item["name"] for item in items]

    typer.echo("Items d'entrée actuels:")
    for item, rate in recipe["input"].items():
        typer.echo(f"{item}: {rate}")
    while True:
        item = typer.prompt(
            "Nom de l'item d'entrée à modifier (ou 'done' pour terminer)"
        )
        if item.lower() == "done":
            break
        if item not in item_names:
            typer.echo(f"L'item '{item}' n'existe pas. Veuillez réessayer.")
            continue
        rate = float(typer.prompt(f"Nouveau taux de {item} par minute"))
        recipe["input"][item] = rate

    typer.echo("Items de sortie actuels:")
    for item, rate in recipe["output"].items():
        typer.echo(f"{item}: {rate}")
    while True:
        item = typer.prompt(
            "Nom de l'item de sortie à modifier (ou 'done' pour terminer)"
        )
        if item.lower() == "done":
            break
        if item not in item_names:
            typer.echo(f"L'item '{item}' n'existe pas. Veuillez réessayer.")
            continue
        rate = float(typer.prompt(f"Nouveau taux de {item} par minute"))
        recipe["output"][item] = rate

    save_data("recipes.json", recipes)
    typer.echo("Recette modifiée avec succès!")


@app.command()
def delete(name: Annotated[str, typer.Option(prompt="Nom de la recette à supprimer")]):
    recipes = load_data("recipes.json")
    recipes = [recipe for recipe in recipes if recipe["name"] != name]
    save_data("recipes.json", recipes)
    typer.echo("Recette supprimée avec succès!")


@app.command()
def list():
    recipes = load_data("recipes.json")
    table = Table(title="Recipes")
    table.add_column("Machine", justify="left")
    table.add_column("Name", justify="left")
    table.add_column("Input", justify="left")
    table.add_column("Output", justify="left")

    for recipe in recipes:
        name = recipe["name"]
        machine = recipe["machine"]
        input_items = ", ".join(
            [f"{item}: {rate}/min" for item, rate in recipe["input"].items()]
        )
        output_items = ", ".join(
            [f"{item}: {rate}/min" for item, rate in recipe["output"].items()]
        )
        table.add_row(machine, name, input_items, output_items)

    console = Console()
    console.print(table)
