import typer

import app.data as data
import app.search as search

app = typer.Typer()
app.add_typer(data.app, name="data")
app.add_typer(search.app, name="search")

if __name__ == "__main__":
    app()
