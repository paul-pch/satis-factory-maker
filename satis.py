import typer

import app.data as data

app = typer.Typer()
app.add_typer(data.app, name="data")

if __name__ == "__main__":
    app()
