from unittest.mock import patch
from typer.testing import CliRunner
from app.build import app


class TestBuildItem:
    runner = CliRunner()
    fake_data = {
        "items": [
            {
                "name": "Test Item 1",
                "key_name": "test_item_1",
            },
            {
                "name": "Test Item 3",
                "key_name": "test_item_3",
            },
        ],
        "recipes": [
            {
                "name": "Test Recipe 1",
                "key_name": "test_recipe_1",
                "ingredients": [["ingedient_1", 1]],
                "category": "fakefactory",
                "time": 2,
                "products": [
                    ["test_item_1", 1],
                ],
            },
            {
                "name": "Test Recipe 2",
                "key_name": "test_recipe_2",
                "ingredients": [["ingedient_2", 1]],
                "category": "fakefactory",
                "time": 2,
                "products": [
                    ["test_item_2", 1],
                ],
            },
        ],
    }

    @patch("app.build.load_data")
    def test_should_build_existing_item(self, mock_load_data):
        mock_load_data.return_value = self.fake_data
        result = self.runner.invoke(
            app, ["--query", "test_item_1", "--minute-rate", "30"]
        )
        assert result.exit_code == 0

    @patch("app.build.load_data")
    def test_should_not_build_non_existing_item(self, mock_load_data):
        mock_load_data.return_value = self.fake_data
        result = self.runner.invoke(
            app, ["--query", "non_existing_item", "--minute-rate", "30"]
        )
        assert result.exit_code == 0
        assert "Item 'non_existing_item' not found." in result.output

    @patch("app.build.load_data")
    def test_should_not_build_item_without_recipe(self, mock_load_data):
        mock_load_data.return_value = self.fake_data
        result = self.runner.invoke(
            app, ["--query", "test_item_3", "--minute-rate", "30"]
        )
        assert result.exit_code == 0
        assert "No recipe found for item 'test_item_3'." in result.output
