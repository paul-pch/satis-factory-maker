from unittest.mock import patch
from typer.testing import CliRunner
from app.search import app


class TestRecipeSubcommand:
    runner = CliRunner()
    fake_data = {
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
        ]
    }

    @patch("app.search.load_data")
    def test_should_return_an_existing_recipe(self, mock_load_data):
        mock_load_data.return_value = self.fake_data
        result = self.runner.invoke(app, ["recipe", "--query", "iron"])
        assert result.exit_code == 0
        assert "Iron Ingot" in result.output
        assert "iron-ingot" in result.output
        assert "smelting1" in result.output
        assert "30" in result.output
        assert "iron-ore x1" in result.output
        assert "iron-ingot x1" in result.output
        assert "30.00/min" in result.output

    @patch("app.search.load_data")
    def test_should_return_another_existing_recipe(self, mock_load_data):
        mock_load_data.return_value = self.fake_data
        result = self.runner.invoke(app, ["recipe", "--query", "Steel"])
        assert result.exit_code == 0
        assert "Steel Ingot" in result.output
        assert "steel-ingot" in result.output
        assert "smelting2" in result.output
        assert "4" in result.output
        assert "iron-ingot x3" in result.output
        assert "coal x3" in result.output
        assert "3" in result.output
        assert "45.00/min" in result.output

    @patch("app.search.load_data")
    def test_should_not_return_a_non_existing_recipe(self, mock_load_data):
        mock_load_data.return_value = self.fake_data
        result = self.runner.invoke(app, ["recipe", "--query", "Non-existent Recipe"])
        assert result.exit_code == 0
        assert "No recipes found matching 'Non-existent Recipe'" in result.output
