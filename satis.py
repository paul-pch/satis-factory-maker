import typer

from app.item import app as item_app
from app.recipe import app as recipe_app

app = typer.Typer()
app.add_typer(item_app, name="item")
app.add_typer(recipe_app, name="recipe")

if __name__ == "__main__":
    app()
