import typer

import app.build as build
import app.parse as parse
import app.search as search

app = typer.Typer()
app.command()(parse.parse)
app.add_typer(search.app, name="search")
app.add_typer(build.app, name="build")

if __name__ == "__main__":
    app()
