from unittest.mock import patch
from typer.testing import CliRunner
from app.search import app


class TestItemSubcommand:
    def setup_method(self):
        self.runner = CliRunner()
        self.fake_data = {
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
            ]
        }

    @patch("app.search.load_data")
    def test_should_return_an_existing_item(self, mock_load_data):
        mock_load_data.return_value = self.fake_data
        result = self.runner.invoke(app, ["item", "--query", "Test Item 1"])
        assert result.exit_code == 0
        assert "Test Item 1" in result.output
        assert "test_item_1" in result.output
        assert "1" in result.output
        assert "10" in result.output

    @patch("app.search.load_data")
    def test_should_not_return_a_non_existing_item(self, mock_load_data):
        mock_load_data.return_value = self.fake_data
        result = self.runner.invoke(app, ["item", "--query", "Non-existent Item"])
        assert result.exit_code == 0
        assert "No items found matching 'Non-existent Item'" in result.output

    @patch("app.search.load_data")
    def test_should_return_unknown_when_stack_size_not_defined(self, mock_load_data):
        mock_load_data.return_value = self.fake_data
        result = self.runner.invoke(app, ["item", "--query", "Test Item 3"])
        assert result.exit_code == 0
        assert "Test Item 3" in result.output
        assert "test_item_3" in result.output
        assert "3" in result.output
        assert "unknown" in result.output
