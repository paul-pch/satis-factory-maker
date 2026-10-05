# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Python CLI (Typer + Rich) that plans Satisfactory factory production lines for a target item and minute rate, using game data parsed from the game's own `CommunityResources/Docs/en-US.json`. The README holds the feature/bug backlog (partly in French; UI labels are also partly French).

## Commands

```bash
make                      # all: sync + build + integrate (integrate appends dist/ to PATH in ~/.zshrc)
make sync                 # uv sync: creates .venv/ from pyproject.toml + uv.lock (dev group included)
make test                 # uv run pytest
uv run pytest tests/test_search_recipe.py::TestRecipeSubcommand::test_should_return_multiple_recipes
make build                # pyinstaller one-file binary -> dist/satisfactory
uvx ruff check . / uvx ruff format .   # lint config in pyproject.toml (line-length 130); ruff is not a project dependency

uv run satis.py parse --file <Docs.json>                     # parse the game file into data/data.json (--output to change)
uv run satis.py search item --query iron
uv run satis.py search recipe --query iron-plate
uv run satis.py build --query iron-plate --minute-rate 60    # interactive: prompts a recipe choice per item
```

Dependencies are managed with uv (`uv add <pkg>`, `uv add --dev <pkg>`); runtime deps in `[project]`, test/build tooling in the `dev` dependency group. The project is not packaged (`tool.uv.package = false`), so there is no installed `satis` entry point. Run everything from the repo root: `data/data.json` is opened via a relative path.

## Architecture

- `satis.py` mounts three Typer sub-apps: `data` (`app/data.py`), `search` (`app/search.py`), `build` (`app/build.py`). `build` is a callback with `invoke_without_command=True`, so it takes options directly (`satis build --query ...`).
- `app/parse.py` turns the game Docs file (UTF-16 or UTF-8; a list of `{NativeClass, Classes}` groups with Unreal-style string fields such as `ItemClass="…Desc_X_C'",Amount=6`) into the committed `data/data.json`: `key_name` = slugified display name (`alt-` prefix for alternates), fluid amounts converted from liters to m³, production building mapped to the `category` names (`smelting1`, `crafting2`, …), only manufacturer recipes outside seasonal events kept, standard recipes listed before alternates. Regenerate `data/data.json` with `parse` rather than editing it.
- `app/search.py` and `app/build.py` each load `data/data.json` **at import time** into module globals (`ITEMS`, `RECIPES`, `RESOURCES`, `FLUIDS`). Data keys: `belts, pipes, buildings, miners, items, fluids, recipes, resources`. Item/recipe identifiers are `key_name`; recipe `ingredients`/`products` are `[key_name, qty]` pairs and `time` is in seconds, with `category` used as the building.
- `app/models.py`: `Recipe` (TypedDict mirroring the JSON) and `ProductionLine` (dataclass; `merge` sums machines and keeps the max layer).
- Build flow (`app/build.py`): `plan()` recurses from the target item. For each item it lists matching recipes, asks the user to pick one (`choose_recipe` via `typer.prompt`), computes `num_machine = ceil(target_rate / recipe_rate)` where rate = `60 / time * qty`, appends a `ProductionLine` at `layer`, then recurses on every ingredient that is not a resource or fluid at `layer + 1`. `compact()` merges lines per item and sorts by layer; `get_resources_rate()` sums raw resource/fluid consumption. Only `recipe["products"][0]` is treated as the line's output (by-products are ignored).
- `app/utils.py`: `load_data` (raises `typer.Exit` on missing/invalid file) and the Rich table renderers.

## Tests

Tests use `typer.testing.CliRunner` and `@patch("app.search.load_data")`. Because data is loaded at module import, that patch has no effect and tests actually run against the real `data/data.json`; several tests currently fail for this reason (and `test_load_data_file_not_found` expects `FileNotFoundError` while `load_data` raises `typer.Exit`). To mock data, patch the module globals (e.g. `app.search.ITEMS`) or move loading out of import time. `tests/test_build.py` is entirely commented out.
