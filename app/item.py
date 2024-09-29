#!/usr/bin/python3

from typing import Optional

import typer

from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated

from .utils import load_data, save_data, to_lower_snake_case

app = typer.Typer()
console = Console()


@app.command()
def create(
    name: Annotated[str, typer.Option(prompt="Nom de l'item")],
    description: Annotated[str, typer.Option(prompt="Description de l'item")],
    tier: Annotated[
        Optional[int],
        typer.Option(
            prompt="Tier de l'item (0-10, laissez vide pour ne pas spécifier)"
        ),
    ],
):
    items = load_data("items.json")
    name = to_lower_snake_case(name)
    for item in items:
        if item["name"] == name:
            typer.echo(f"L'item '{name}' existe déjà.")
            return

    new_item = {
        "name": name,
        "description": description,
        "tier": tier if tier is not None else None,
    }
    items.append(new_item)
    save_data("items.json", items)
    typer.echo(f"Item '{name}' ajouté avec succès!")


@app.command()
def edit(
    name: Annotated[str, typer.Option(prompt="Nom de l'item à modifier")],
    new_name: Annotated[
        Optional[str], typer.Option(prompt="Nouveau nom de l'item")
    ] = "",
    new_description: Annotated[
        Optional[str], typer.Option(prompt="Nouvelle description de l'item")
    ] = "",
    new_tier: Annotated[
        Optional[int],
        typer.Option(
            prompt="Nouveau tier de l'item (0-10, entrez -1 pour ne pas changer)"
        ),
    ] = -1,
):
    if not new_name and not new_description and new_tier == -1:
        typer.echo("Rien à modifier.")
        return

    items = load_data("items.json")
    name = to_lower_snake_case(name)
    for item in items:
        if item["name"] == name:
            if new_name:
                new_name = to_lower_snake_case(new_name)
                item["name"] = new_name
            if new_description:
                item["description"] = new_description
            if new_tier is not None:
                item["tier"] = new_tier
            save_data("items.json", items)
            typer.echo(f"Item '{name}' modifié avec succès!")
            return
    typer.echo(f"Item '{name}' non trouvé.")


@app.command()
def delete(name: Annotated[str, typer.Option(prompt="Nom de l'item à supprimer")]):
    items = load_data("items.json")
    name = to_lower_snake_case(name)
    item_exists = False

    for i, item in enumerate(items):
        if item["name"] == name:
            items.pop(i)
            item_exists = True
            break

    save_data("items.json", items)

    if item_exists:
        typer.echo(f"Item '{name}' supprimé avec succès!")
    else:
        typer.echo(f"L'item '{name}' n'existait déjà pas !")


@app.command()
def list():
    items = load_data("items.json")
    table = Table(title="Items")
    table.add_column("Nom", justify="left")
    table.add_column("Description", justify="left")
    table.add_column("Tier", justify="center")

    for item in items:
        tier = item.get("tier", "Non spécifié")
        table.add_row(item["name"], item["description"], str(tier))

    console.print(table)
