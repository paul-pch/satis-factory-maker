import pytest
from typer.testing import CliRunner

from app.build import app, check_ingredients, compact, get_minute_rate, get_resources_rate
from app.models import ProductionLine, Recipe

runner = CliRunner()


def rows(output: str) -> list[list[str]]:
    """Cells of every body row of the Rich tables in output."""
    return [[cell.strip() for cell in line.strip("│ ").split("│")] for line in output.splitlines() if line.startswith("│")]


def row(output: str, first_cell: str) -> list[str]:
    """Cells of the Rich table row whose first cell is first_cell."""
    for cells in rows(output):
        if cells[0] == first_cell:
            return cells
    raise AssertionError(f"no row {first_cell!r} in output")


def recipe(data, key_name) -> Recipe:
    return next(r for r in data["recipes"] if r["key_name"] == key_name)


class TestMinuteRate:
    def test_should_compute_product_rate(self, data):
        assert get_minute_rate(recipe(data, "iron-plate"), "iron-plate", "products") == 20

    def test_should_compute_ingredient_rate(self, data):
        assert get_minute_rate(recipe(data, "reinforced-iron-plate"), "screws", "ingredients") == 60

    def test_should_keep_fractional_quantities(self, data):
        fractional: Recipe = {**recipe(data, "iron-ingot"), "ingredients": [("iron-ore", 2.5)]}
        assert get_minute_rate(fractional, "iron-ore", "ingredients") == 75

    def test_should_keep_fractional_time(self, data):
        fractional: Recipe = {**recipe(data, "iron-ingot"), "time": 2.4}
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

    def test_should_import_an_item_instead_of_producing_it(self, patched_data):
        # reinforced-iron-plate, iron-plate, iron-ingot, then screws imported (choice 0)
        result = runner.invoke(app, ["--query", "reinforced-iron-plate", "--minute-rate", "5"], input="1\n1\n1\n0\n")
        assert result.exit_code == 0, result.output
        factory, rest = result.output.split("Factory")[-1].split("Ressources requises")
        resources, imports = rest.split("Imports en gare")
        assert [cells[1] for cells in rows(factory)] == ["reinforced-iron-plate", "iron-plate", "iron-ingot"]
        assert row(resources, "iron-ore") == ["iron-ore", "60.0"]
        assert row(imports, "screws") == ["screws", "60.0"]

    def test_should_sum_imports_of_the_same_item(self, patched_data):
        # iron-ingot is imported twice: 60/min for the plates and 30/min for the rods
        result = runner.invoke(app, ["--query", "reinforced-iron-plate", "--minute-rate", "5"], input="1\n1\n0\n1\n1\n0\n")
        assert result.exit_code == 0, result.output
        factory, rest = result.output.split("Factory")[-1].split("Ressources requises")
        resources, imports = rest.split("Imports en gare")
        assert [cells[1] for cells in rows(factory)] == ["reinforced-iron-plate", "iron-plate", "screws", "iron-rod"]
        assert "iron-ore" not in resources
        assert row(imports, "iron-ingot") == ["iron-ingot", "90.0"]

    def test_should_not_display_imports_when_nothing_is_imported(self, patched_data):
        result = runner.invoke(app, ["--query", "iron-ingot", "--minute-rate", "30"], input="1\n")
        assert result.exit_code == 0, result.output
        assert "Imports en gare" not in result.output

    def test_should_offer_import_as_choice_zero(self, patched_data):
        result = runner.invoke(app, ["--query", "iron-ingot", "--minute-rate", "30"], input="0\n")
        assert result.exit_code == 0, result.output
        assert "[0] import" in result.output
        assert row(result.output.split("Imports en gare")[-1], "iron-ingot") == ["iron-ingot", "30.0"]

    def test_should_number_recipes_in_the_matching_table(self, patched_data):
        result = runner.invoke(app, ["--query", "iron-plate", "--minute-rate", "20"], input="1\n1\n")
        assert result.exit_code == 0, result.output
        matching = result.output.split("Matching recipes")[1].split("Choose a recipe")[0]
        assert [cells[:2] for cells in rows(matching)] == [["1", "Iron Plate"], ["2", "Alternate: Iron Wire Plate"]]

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


class TestFactoryId:
    def test_should_print_the_factory_id(self, patched_data):
        # reinforced-iron-plate, iron-plate (alternate), iron-ingot, then screws imported
        result = runner.invoke(app, ["--query", "reinforced-iron-plate", "--minute-rate", "5"], input="1\n2\n1\n0\n")
        assert result.exit_code == 0, result.output
        assert "ID usine : reinforced-iron-plate:1210" in result.output

    def test_should_rebuild_the_factory_without_prompting(self, patched_data):
        prompted = runner.invoke(app, ["--query", "reinforced-iron-plate", "--minute-rate", "5"], input="1\n2\n1\n0\n")
        replayed = runner.invoke(app, ["--id", "reinforced-iron-plate:1210", "--minute-rate", "5"])
        assert replayed.exit_code == 0, replayed.output
        assert "Choose a recipe" not in replayed.output
        assert replayed.output.split("Factory")[-1] == prompted.output.split("Factory")[-1]

    def test_should_rebuild_the_factory_at_another_rate(self, patched_data):
        # Same choices as test_should_compute_machines_and_resources, at twice the rate
        result = runner.invoke(app, ["--id", "iron-plate:21", "--minute-rate", "120"])
        assert result.exit_code == 0, result.output
        factory, resources = result.output.split("Factory")[-1].split("Ressources requises")
        assert row(factory, "0")[1:4] == ["iron-plate", "crafting1", "3"]
        assert row(factory, "1")[1:4] == ["iron-ingot", "smelting1", "6"]
        assert row(resources, "water") == ["water", "90.0"]
        assert "ID usine : iron-plate:21" in result.output

    def test_should_accept_a_matching_query(self, patched_data):
        result = runner.invoke(app, ["--query", "iron-ingot", "--id", "iron-ingot:1", "--minute-rate", "30"])
        assert result.exit_code == 0, result.output

    def test_should_fail_when_query_and_id_disagree(self, patched_data):
        result = runner.invoke(app, ["--query", "iron-plate", "--id", "iron-ingot:1", "--minute-rate", "30"])
        assert result.exit_code == 1
        assert "Factory ID builds 'iron-ingot', not 'iron-plate'." in result.output

    @pytest.mark.parametrize("factory_id", ["iron-plate:2", "iron-plate:211", "iron-plate:31", "iron-plate:2!", "21"])
    def test_should_fail_on_invalid_id(self, patched_data, factory_id):
        result = runner.invoke(app, ["--id", factory_id, "--minute-rate", "30"])
        assert result.exit_code == 1
        assert "Invalid factory ID" in result.output

    def test_should_require_query_or_id(self, patched_data):
        result = runner.invoke(app, ["--minute-rate", "30"])
        assert result.exit_code == 1
        assert "Missing option '--query' (or '--id')." in result.output

    @pytest.mark.parametrize("factory_id", ["iron-plate:::21", "iron-plate"])
    def test_should_fail_on_malformed_id(self, patched_data, factory_id):
        result = runner.invoke(app, ["--id", factory_id, "--minute-rate", "30"])
        assert result.exit_code == 1
        assert "Invalid factory ID" in result.output


class TestRecipeModes:
    # iron-ingot is needed twice: by iron-plate and by iron-rod (for the screws)
    def test_should_reuse_the_recipe_chosen_for_an_item(self, patched_data):
        result = runner.invoke(app, ["--query", "reinforced-iron-plate", "--minute-rate", "5"], input="1\n1\n1\n1\n1\n")
        assert result.exit_code == 0, result.output
        assert result.output.count("Choose a recipe") == 5
        assert "ID usine : reinforced-iron-plate:11111" in result.output

    def test_should_reuse_an_import_choice(self, patched_data):
        result = runner.invoke(app, ["--query", "reinforced-iron-plate", "--minute-rate", "5"], input="1\n1\n0\n1\n1\n")
        assert result.exit_code == 0, result.output
        assert result.output.count("Choose a recipe") == 5
        assert row(result.output.split("Imports en gare")[-1], "iron-ingot") == ["iron-ingot", "90.0"]

    def test_should_ask_every_node_in_complex_mode(self, patched_data):
        # The plates' ingots are imported, the rods' ingots are smelted
        args = ["--query", "reinforced-iron-plate", "--minute-rate", "5", "--complex"]
        result = runner.invoke(app, args, input="1\n1\n0\n1\n1\n1\n")
        assert result.exit_code == 0, result.output
        assert result.output.count("Choose a recipe") == 6
        assert row(result.output.split("Imports en gare")[-1], "iron-ingot") == ["iron-ingot", "60.0"]
        assert "ID usine : reinforced-iron-plate::110111" in result.output

    def test_should_replay_a_complex_mode_id(self, patched_data):
        prompted = runner.invoke(
            app, ["--query", "reinforced-iron-plate", "--minute-rate", "5", "--complex"], input="1\n1\n0\n1\n1\n1\n"
        )
        replayed = runner.invoke(app, ["--id", "reinforced-iron-plate::110111", "--minute-rate", "5"])
        assert replayed.exit_code == 0, replayed.output
        assert "Choose a recipe" not in replayed.output
        assert replayed.output.split("Factory")[-1] == prompted.output.split("Factory")[-1]

    def test_should_fail_on_complex_flag_with_a_simple_mode_id(self, patched_data):
        result = runner.invoke(app, ["--id", "iron-plate:11", "--minute-rate", "30", "--complex"])
        assert result.exit_code == 1
        assert "--complex given with a simple mode factory ID." in result.output
