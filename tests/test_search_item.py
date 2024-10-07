import unittest
from unittest.mock import patch, mock_open
import json
from typer.testing import CliRunner
from app.search import app

test_data = {
    "items": [
        {
            "name": "Iron Ore",
            "key_name": "iron-ore",
            "tier": -1,
            "stack_size": 100,
        },
        {
            "name": "Steel Ingot",
            "key_name": "steel-ingot",
            "tier": 0,
            "stack_size": 50,
        },
    ]
}


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps(test_data))
    def test_item_search(self, mock_file):
        result = self.runner.invoke(app, ["item", "Iron"])
        self.assertIn("Iron Ore", result.output)
        self.assertNotIn("Steel Ingot", result.output)

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_file_not_found(self, mock_file):
        result = self.runner.invoke(app, ["item", "Iron"])
        self.assertIn("Data file not found", result.output)

    @patch(
        "json.load",
        side_effect=json.JSONDecodeError(
            "Expecting value: line 1 column 1 (char 0)", "", 0
        ),
    )
    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_json_decode_error(self, mock_file, mock_json):
        result = self.runner.invoke(app, ["item", "Iron"])
        self.assertIn("Error decoding JSON data", result.output)


if __name__ == "__main__":
    unittest.main()
