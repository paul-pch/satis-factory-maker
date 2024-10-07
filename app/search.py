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
