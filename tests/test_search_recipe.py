from app.search import app
from click.testing import Result
from typer.testing import CliRunner
from typing import Any
from unittest.mock import MagicMock, patch

Json = dict[str, Any]


class TestRecipeSubcommand:
    runner = CliRunner()
    fake_data: Json = {
        "recipes": [
            {
                "name": "Iron Ingot",
                "key_name": "iron-ingot",
                "category": "smelting1",
                "time": 2,
                "ingredients": [["iron-ore", 1]],
                "products": [["iron-ingot", 1]],
            },
            {
                "name": "Steel Ingot",
                "key_name": "steel-ingot",
                "category": "smelting2",
                "time": 4,
                "ingredients": [["iron-ingot", 3], ["coal", 3]],
                "products": [["steel-ingot", 3]],
            },
            {
                "name": "Steel Ingot4",
                "key_name": "steel-ingot4",
                "category": "smelting4",
                "time": 4,
                "ingredients": [["iron-ingot", 3], ["coal", 3]],
                "products": [["steel-ingot", 3]],
            },
        ]
    }

    def assert_recipe1(self, result: Result) -> None:
        assert "Iron Ingot" in result.output
        assert "iron-ingot" in result.output
        assert "smelting1" in result.output
        assert "30" in result.output
        assert "iron-ore x1" in result.output
        assert "iron-ingot x1" in result.output
        assert "30.00/min" in result.output

    def assert_recipe2(self, result: Result) -> None:
        assert "Steel Ingot" in result.output
        assert "steel-ingot" in result.output
        assert "smelting2" in result.output
        assert "4" in result.output
        assert "iron-ingot x3" in result.output
        assert "coal x3" in result.output
        assert "3" in result.output
        assert "45.00/min" in result.output

    def assert_recipe4(self, result: Result) -> None:
        assert "Steel Ingot4" in result.output
        assert "steel-ingot4" in result.output
        assert "smelting4" in result.output
        assert "4" in result.output
        assert "iron-ingot x3" in result.output
        assert "coal x3" in result.output
        assert "3" in result.output
        assert "45.00/min" in result.output

    @patch("app.search.load_data")
    def test_should_return_an_existing_recipe(self, mock_load_data: MagicMock):
        mock_load_data.return_value = self.fake_data
        result = self.runner.invoke(app, ["recipe", "--query", "iron"])
        assert result.exit_code == 0
        self.assert_recipe1(result)

    @patch("app.search.load_data")
    def test_should_return_an_existing_recipe_with_dash(self, mock_load_data: MagicMock):
        mock_load_data.return_value = self.fake_data
        result = self.runner.invoke(app, ["recipe", "--query", "iron-ingot"])
        assert result.exit_code == 0
        self.assert_recipe1(result)

    @patch("app.search.load_data")
    def test_should_return_another_existing_recipe(self, mock_load_data: MagicMock):
        mock_load_data.return_value = self.fake_data
        result = self.runner.invoke(app, ["recipe", "--query", "Steel"])
        assert result.exit_code == 0
        self.assert_recipe2(result)

    @patch("app.search.load_data")
    def test_should_not_return_a_non_existing_recipe(self, mock_load_data: MagicMock):
        mock_load_data.return_value = self.fake_data
        result = self.runner.invoke(app, ["recipe", "--query", "Non-existent Recipe"])
        assert result.exit_code == 0
        assert "No recipes found matching 'Non-existent Recipe'" in result.output

    @patch("app.search.load_data")
    def test_should_return_multiple_recipes(self, mock_load_data: MagicMock):
        mock_load_data.return_value = self.fake_data
        result = self.runner.invoke(app, ["recipe", "--query", "steel-ingot"])
        assert result.exit_code == 0
        self.assert_recipe2(result)
        self.assert_recipe4(result)

    @patch("app.search.load_data")
    def test_should_return_only_recipe_with_query_as_output(self, mock_load_data: MagicMock):
        mock_load_data.return_value = self.fake_data
        result = self.runner.invoke(app, ["recipe", "--query", "iron-ingot", "--output"])
        assert result.exit_code == 0
