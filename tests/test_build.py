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
        ],
        "recipes": [
            {
                "name": "Test Recipe 1",
                "products": [
                    ["test_item_1", 1],
                ],
            },
        ],
    }

    @patch("app.build.load_data")
    def test_should_build_existing_item(self, mock_load_data):
        mock_load_data.return_value = self.fake_data
        result = self.runner.invoke(app, ["--query", "test_item_1"])
        assert result.exit_code == 0

    @patch("app.build.load_data")
    def test_should_not_build_non_existing_item(self, mock_load_data):
        mock_load_data.return_value = self.fake_data
        result = self.runner.invoke(app, ["--query", "non_existing_item"])
        assert result.exit_code == 0
        assert "Item 'non_existing_item' not found." in result.output
