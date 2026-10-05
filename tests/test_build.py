import pytest
from typer.testing import CliRunner

from app.build import app, check_ingredients, compact, get_minute_rate, get_resources_rate
from app.models import ProductionLine

runner = CliRunner()


def row(output: str, first_cell: str) -> list[str]:
    """Cells of the Rich table row whose first cell is first_cell."""
    for line in output.splitlines():
        cells = [cell.strip() for cell in line.strip("│ ").split("│")]
        if cells[0] == first_cell:
            return cells
    raise AssertionError(f"no row {first_cell!r} in output")


def recipe(data, key_name):
    return next(r for r in data["recipes"] if r["key_name"] == key_name)


class TestMinuteRate:
    def test_should_compute_product_rate(self, data):
        assert get_minute_rate(recipe(data, "iron-plate"), "iron-plate", "products") == 20

    def test_should_compute_ingredient_rate(self, data):
        assert get_minute_rate(recipe(data, "reinforced-iron-plate"), "screws", "ingredients") == 60

    def test_should_keep_fractional_quantities(self, data):
        fractional = {**recipe(data, "iron-ingot"), "ingredients": [["iron-ore", 2.5]]}
        assert get_minute_rate(fractional, "iron-ore", "ingredients") == 75

    def test_should_keep_fractional_time(self, data):
        fractional = {**recipe(data, "iron-ingot"), "time": 2.4}
        assert get_minute_rate(fractional, "iron-ingot", "products") == pytest.approx(25)


class TestIngredients:
    def test_should_return_crafted_ingredients(self, patched_data):
        assert check_ingredients(recipe(patched_data, "reinforced-iron-plate")) == ["iron-plate", "screws"]

    def test_should_ignore_resources_and_fluids(self, patched_data):
        assert check_ingredients(recipe(patched_data, "alt-iron-wire-plate")) == ["iron-ingot"]
        assert check_ingredients(recipe(patched_data, "iron-ingot")) == []


class TestFactory:
    def test_should_merge_lines_of_the_same_item(self, data):
        ingot = recipe(data, "iron-ingot")
        factory = [
            ProductionLine("iron-plate", "crafting1", 2, recipe(data, "iron-plate"), 1),
            ProductionLine("iron-ingot", "smelting1", 2, ingot, 2),
            ProductionLine("iron-ingot", "smelting1", 1, ingot, 3),
        ]
        merged = compact(factory)
        assert [(line.item, line.num_machine, line.layer) for line in merged] == [
            ("iron-plate", 2, 1),
            ("iron-ingot", 3, 3),
        ]

    def test_should_sum_raw_resources(self, patched_data):
        factory = [
            ProductionLine("iron-ingot", "smelting1", 3, recipe(patched_data, "iron-ingot"), 1),
            ProductionLine("iron-plate", "crafting1", 1, recipe(patched_data, "alt-iron-wire-plate"), 0),
        ]
        assert get_resources_rate(factory) == {"iron-ore": 90, "water": 30}


class TestBuildCommand:
    def test_should_plan_the_whole_chain(self, patched_data):
        # A recipe is asked for every item: always pick the first (standard) one
        result = runner.invoke(app, ["--query", "reinforced-iron-plate", "--minute-rate", "5"], input="1\n" * 6)
        assert result.exit_code == 0, result.output
        factory = result.output.split("Factory")[-1]
        for item in ("reinforced-iron-plate", "iron-plate", "screws", "iron-rod", "iron-ingot"):
            assert item in factory
        assert "iron-ore" in result.output.split("Ressources requises")[-1]

    def test_should_compute_machines_and_resources(self, patched_data):
        # 60 plates/min with the alternate recipe (40/min per machine) -> 2 machines,
        # consuming 2 x 60 = 120 ingots/min (30/min per smelter) -> 4 smelters and 2 x 30 = 60 water/min
        result = runner.invoke(app, ["--query", "iron-plate", "--minute-rate", "60"], input="2\n1\n")
        assert result.exit_code == 0, result.output
        factory, resources = result.output.split("Factory")[-1].split("Ressources requises")
        assert row(factory, "0")[1:4] == ["iron-plate", "crafting1", "2"]
        assert row(factory, "1")[1:4] == ["iron-ingot", "smelting1", "4"]
        assert row(resources, "iron-ore") == ["iron-ore", "120.0"]
        assert row(resources, "water") == ["water", "60.0"]

    def test_should_fail_on_unknown_item(self, patched_data):
        result = runner.invoke(app, ["--query", "copper-plate", "--minute-rate", "10"])
        assert result.exit_code == 1
        assert "Item 'copper-plate' not found." in result.output

    def test_should_fail_on_invalid_recipe_choice(self, patched_data):
        result = runner.invoke(app, ["--query", "iron-plate", "--minute-rate", "10"], input="9\n")
        assert result.exit_code == 1
        assert "Invalid choice." in result.output

    def test_should_require_minute_rate(self, patched_data):
        result = runner.invoke(app, ["--query", "iron-plate"])
        assert result.exit_code == 2
        assert "--minute-rate" in result.output
