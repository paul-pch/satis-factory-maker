import typer
from utils import load_data, save_data
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

@app.command()
def create(
    name: str = typer.Option(..., prompt="Nom de l'item"),
    description: str = typer.Option(..., prompt="Description de l'item"),
    tier: int = typer.Option(None, prompt="Tier de l'item (0-10, laissez vide pour ne pas spécifier)")
):
    items = load_data('items.json')
    for item in items:
        if item['name'] == name:
            typer.echo(f"L'item '{name}' existe déjà.")
            return

    new_item = {
        "name": name,
        "description": description,
        "tier": tier if tier is not None else None
    }
    items.append(new_item)
    save_data('items.json', items)
    typer.echo(f"Item '{name}' ajouté avec succès!")

@app.command()
def edit(
    name: str = typer.Option(..., prompt="Nom de l'item à modifier"),
    new_name: str = typer.Option(None, prompt="Nouveau nom de l'item (laissez vide pour ne pas changer)"),
    new_description: str = typer.Option(None, prompt="Nouvelle description de l'item (laissez vide pour ne pas changer)"),
    new_tier: int = typer.Option(None, prompt="Nouveau tier de l'item (0-10, laissez vide pour ne pas changer)")
):
    items = load_data('items.json')
    for item in items:
        if item['name'] == name:
            if new_name:
                item['name'] = new_name
            if new_description:
                item['description'] = new_description
            if new_tier is not None:
                item['tier'] = new_tier
            save_data('items.json', items)
            typer.echo(f"Item '{name}' modifié avec succès!")
            return
    typer.echo(f"Item '{name}' non trouvé.")

@app.command()
def delete(
    name: str = typer.Option(..., prompt="Nom de l'item à supprimer")
):
    items = load_data('items.json')
    items = [item for item in items if item['name'] != name]
    save_data('items.json', items)
    typer.echo(f"Item '{name}' supprimé avec succès!")

@app.command()
def show():
    items = load_data('items.json')
    table = Table(title="Items")
    table.add_column("Nom", justify="left")
    table.add_column("Description", justify="left")
    table.add_column("Tier", justify="center")

    for item in items:
        tier = item.get('tier', 'Non spécifié')
        table.add_row(item['name'], item['description'], str(tier))

    console.print(table)
