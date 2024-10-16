import typer

import app.data as data
import app.search as search
import app.build as build

app = typer.Typer()
app.add_typer(data.app, name="data")
app.add_typer(search.app, name="search")
app.add_typer(build.app, name="build")

if __name__ == "__main__":
    app()
