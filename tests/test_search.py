from typer.testing import CliRunner

from app.search import app

runner = CliRunner()


class TestSearchItem:
    def test_should_find_item_by_name_ignoring_case(self, patched_data):
        result = runner.invoke(app, ["item", "--query", "IRON PLATE"])
        assert result.exit_code == 0
        assert "Iron Plate" in result.output
        assert "iron-plate" in result.output

    def test_should_find_item_by_key_name(self, patched_data):
        result = runner.invoke(app, ["item", "--query", "iron-rod"])
        assert result.exit_code == 0
        assert "Iron Rod" in result.output

    def test_should_list_every_matching_item(self, patched_data):
        result = runner.invoke(app, ["item", "--query", "iron"])
        assert result.exit_code == 0
        for name in ("Iron Ore", "Iron Ingot", "Iron Plate", "Iron Rod", "Reinforced Iron Plate"):
            assert name in result.output
        assert "Screws" not in result.output

    def test_should_display_unknown_when_stack_size_is_missing(self, patched_data, data):
        del data["items"][-1]["stack_size"]
        result = runner.invoke(app, ["item", "--query", "mystery"])
        assert result.exit_code == 0
        assert "unknown" in result.output

    def test_should_report_no_match(self, patched_data):
        result = runner.invoke(app, ["item", "--query", "copper"])
        assert result.exit_code == 0
        assert "No items found matching 'copper'" in result.output


class TestSearchRecipe:
    def test_should_find_recipe_by_name_with_rates(self, patched_data):
        result = runner.invoke(app, ["recipe", "--query", "Iron Ingot"])
        assert result.exit_code == 0
        assert "smelting1" in result.output
        assert "iron-ore x1" in result.output
        assert "30.00/min" in result.output

    def test_should_find_recipes_producing_the_item(self, patched_data):
        result = runner.invoke(app, ["recipe", "--query", "iron-plate"])
        assert result.exit_code == 0
        assert "alt-iron-wire-plate" in result.output
        assert "20.00/min" in result.output  # standard recipe: 2 plates / 6 s
        assert "40.00/min" in result.output  # alternate recipe: 4 plates / 6 s

    def test_should_not_number_recipes(self, patched_data):
        result = runner.invoke(app, ["recipe", "--query", "Iron Ingot"])
        assert result.exit_code == 0
        assert "#" not in result.output

    def test_should_report_no_match(self, patched_data):
        result = runner.invoke(app, ["recipe", "--query", "copper"])
        assert result.exit_code == 0
        assert "No recipes found matching 'copper'" in result.output
