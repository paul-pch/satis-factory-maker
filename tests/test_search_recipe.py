import json
import os
import tempfile

from typer.testing import CliRunner
from app.search import app


class TestRecipeSubcommand:
    def setup_method(self):
        self.runner = CliRunner()
        self.fake_data = {
            "recipes": [
                {
                    "name": "Iron Ingot",
                    "key_name": "iron-ingot",
                    "category": "smelting1",
                    "time": 120,
                    "ingredients": [["iron-ore", 1]],
                    "products": [["iron-ingot", 1]],
                },
                {
                    "name": "Steel Ingot",
                    "key_name": "steel-ingot",
                    "category": "smelting2",
                    "time": 180,
                    "ingredients": [["iron-ingot", 1], ["coal", 1]],
                    "products": [["steel-ingot", 1]],
                },
            ]
        }
        self.temp_dir = tempfile.mkdtemp()
        with open(os.path.join(self.temp_dir, "data.json"), "w", encoding="utf-8") as f:
            json.dump(self.fake_data, f)

    def test_recipe_search(self):
        result = self.runner.invoke(app, ["recipe", "--query", "iron"])
        print(result.output)
        assert result.exit_code == 0
        assert "Iron Ingot" in result.output
        assert "iron-ingot" in result.output
        assert "smelting1" in result.output
        assert "120" in result.output
        assert "iron-ore x1" in result.output
        assert "iron-ingot x1" in result.output
        assert "0.50/min" in result.output
        assert "1.00/min" in result.output

        result = self.runner.invoke(app, ["recipe", "--query", "Steel"])
        assert result.exit_code == 0
        assert "Steel Ingot" in result.output
        assert "steel-ingot" in result.output
        assert "smelting2" in result.output
        assert "180" in result.output
        assert "iron-ingot x1" in result.output
        assert "coal x1" in result.output
        assert "0.33/min" in result.output
        assert "0.56/min" in result.output
        assert "1.00/min" in result.output

        result = self.runner.invoke(app, ["recipe", "--query", "Non-existent Recipe"])
        assert result.exit_code == 0
        assert "No recipes found matching 'Non-existent Recipe'" in result.output
