#!/usr/bin/python3

import json
import typer
import requests

from rich.console import Console
from typing_extensions import Annotated

app = typer.Typer()
console = Console()


@app.command()
def fetch(
    url: Annotated[
        str, typer.Option()
    ] = "https://raw.githubusercontent.com/KirkMcDonald/satisfactory-calculator/master/data/data.json"
):
    """
    Fetch the JSON data from the given URL and save it locally.
    """
    try:
        print(f"{url}")
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        with open("data/data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        console.print("[green]Data fetched and saved successfully![/green]")
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error fetching data: {e}[/red]")
