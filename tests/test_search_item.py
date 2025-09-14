from app.search import app
from typer.testing import CliRunner
from typing import Any
from unittest.mock import MagicMock, patch

Json = dict[str, Any]


class TestItemSubcommand:
    runner = CliRunner()
    fake_data: Json = {
        "items": [
            {
                "name": "Test Item 1",
                "key_name": "test_item_1",
                "tier": 1,
                "stack_size": 10,
            },
            {
                "name": "Test Item 2",
                "key_name": "test_item_2",
                "tier": 2,
                "stack_size": 20,
            },
            {
                "name": "Test Item 3",
                "key_name": "test_item_3",
                "tier": 3,
            },
            {
                "name": "Test Item 4",
                "key_name": "test-item-4",
                "tier": 4,
            }
        ]
    }

    @patch("app.search.load_data")
    def test_should_return_an_existing_item_with_spaces(self, mock_load_data: MagicMock):
        mock_load_data.return_value = self.fake_data
        result = self.runner.invoke(app, ["item", "--query", "Test Item 1"])
        assert result.exit_code == 0
        assert "Test Item 1" in result.output
        assert "test_item_1" in result.output
        assert "1" in result.output
        assert "10" in result.output

    @patch("app.search.load_data")
    def test_should_return_another_existing_item_with_dash(self, mock_load_data: MagicMock):
        mock_load_data.return_value = self.fake_data
        result = self.runner.invoke(app, ["item", "--query", "item-4"])
        assert result.exit_code == 0
        assert "Test Item 4" in result.output
        assert "test-item-4" in result.output
        assert "4" in result.output

    @patch("app.search.load_data")
    def test_should_return_multiple_items_if_many(self, mock_load_data: MagicMock):
        mock_load_data.return_value = self.fake_data
        result = self.runner.invoke(app, ["item", "--query", "item"])
        assert result.exit_code == 0
        assert "Test Item 3" in result.output
        assert "Test Item 4" in result.output
        assert "10" in result.output

    @patch("app.search.load_data")
    def test_should_not_return_a_non_existing_item(self, mock_load_data: MagicMock):
        mock_load_data.return_value = self.fake_data
        result = self.runner.invoke(app, ["item", "--query", "Non-existent Item"])
        assert result.exit_code == 0
        assert "No items found matching 'Non-existent Item'" in result.output

    @patch("app.search.load_data")
    def test_should_return_unknown_when_stack_size_not_defined(self, mock_load_data: MagicMock):
        mock_load_data.return_value = self.fake_data
        result = self.runner.invoke(app, ["item", "--query", "Test Item 3"])
        assert result.exit_code == 0
        assert "Test Item 3" in result.output
        assert "test_item_3" in result.output
        assert "3" in result.output
        assert "unknown" in result.output
