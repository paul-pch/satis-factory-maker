import typer

from item import app as item_app

app = typer.Typer()
app.add_typer(item_app, name="item")

if __name__ == "__main__":
    app()
