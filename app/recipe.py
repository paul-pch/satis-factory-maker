import typer
import json
from tabulate import tabulate
from .utils import load_data, save_data

app = typer.Typer()

@app.command()
def add(
    name: str = typer.Option(..., prompt="Nom de la recette"),
    machine: str = typer.Option(..., prompt="Machine"),
):
    input_items = {}
    output_items = {}

    while True:
        item = typer.prompt("Nom de l'item d'entrée (ou 'done' pour terminer)")
        if item.lower() == 'done':
            break
        rate = float(typer.prompt(f"Taux de {item} par minute"))
        input_items[item] = rate

    while True:
        item = typer.prompt("Nom de l'item de sortie (ou 'done' pour terminer)")
        if item.lower() == 'done':
            break
        rate = float(typer.prompt(f"Taux de {item} par minute"))
        output_items[item] = rate

    recipe = {
        "name": name,
        "machine": machine,
        "input": input_items,
        "output": output_items
    }

    recipes = load_data('recipes.json')
    recipes.append(recipe)
    save_data('recipes.json', recipes)
    typer.echo("Recette ajoutée avec succès!")

@app.command()
def list():
    recipes = load_data('recipes.json')
    table = []

    for recipe in recipes:
        name = recipe['name']
        machine = recipe['machine']
        input_items = ', '.join([f"{item}: {rate}/min" for item, rate in recipe['input'].items()])
        output_items = ', '.join([f"{item}: {rate}/min" for item, rate in recipe['output'].items()])
        table.append([machine, name, input_items, output_items])

    typer.echo(tabulate(table, headers=["Machine", "Nom", "Entrée", "Sortie"], tablefmt="pipe"))
