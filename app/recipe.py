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
    new_name: Annotated[
        Optional[str],
        typer.Option(
            prompt="Nouveau nom de la recette (laissez vide pour ne pas changer)"
        ),
    ] = "",
    new_machine: Annotated[
        Optional[str],
        typer.Option(prompt="Nouvelle machine (laissez vide pour ne pas changer)"),
    ] = "",
    new_input: Annotated[
        Optional[str],
        typer.Option(
            prompt="Nouveaux items d'entrée (séparés par des virgules, laissez vide pour ne pas changer)"
        ),
    ] = "",
    new_output: Annotated[
        Optional[str],
        typer.Option(
            prompt="Nouveaux items de sortie (séparés par des virgules, laissez vide pour ne pas changer)"
        ),
    ] = "",
):
    recipes = load_data("recipes.json")

    for recipe in recipes:
        if recipe["name"] == name:
            if new_name:
                recipe["name"] = new_name
            if new_machine:
                recipe["machine"] = new_machine
            if new_input:
                recipe["input"] = {
                    item: float(rate)
                    for item, rate in (pair.split(":") for pair in new_input.split(","))
                }
            if new_output:
                recipe["output"] = {
                    item: float(rate)
                    for item, rate in (
                        pair.split(":") for pair in new_output.split(",")
                    )
                }

            save_data("recipes.json", recipes)
            typer.echo("Recette modifiée avec succès!")
            return

    typer.echo(f"Recette '{name}' non trouvée.")


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
