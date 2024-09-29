import json
import os
import tempfile
import unittest
from unittest.mock import patch

from typer.testing import CliRunner

from app.item import app
from app.utils import load_data, save_data


class TestItemDelete(unittest.TestCase):
    def setUp(self):
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(
            b'[{"name": "item1", "description": "description1", "tier": 1}, {"name": "item2", "description": "description2"}]'
        )
        self.temp_file.close()

        # Patch the load_data and save_data functions to use the temporary file
        self.load_data_patch = patch(
            "app.item.load_data", side_effect=lambda _: load_data(self.temp_file.name)
        )
        self.save_data_patch = patch(
            "app.item.save_data",
            side_effect=lambda file_path, data: save_data(self.temp_file.name, data),
        )
        self.load_data_patch.start()
        self.save_data_patch.start()

    def tearDown(self):
        # Clean up the temporary file
        os.remove(self.temp_file.name)
        self.load_data_patch.stop()
        self.save_data_patch.stop()

    def test_should_delete_existing_item(self):
        runner = CliRunner()
        result = runner.invoke(app, ["delete", "--name", "item1"])
        print("toto")
        print(result.exit_code)
        print(result.stdout)

        # Check that the command was successful
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Item 'item1' supprimé avec succès!", result.stdout)

        # Check that the item was deleted from the temporary file
        with open(self.temp_file.name, "r", encoding="UTF-8") as f:
            data = json.load(f)
            print(data)
            print(len(data))
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["name"], "item2")

    def test_should_not_delete_nonexistent_with_regular_message(self):
        runner = CliRunner()
        result = runner.invoke(app, ["delete", "--name", "nonexistent"])

        # Check that the command was successful
        self.assertEqual(result.exit_code, 0)
        self.assertIn("L'item 'nonexistent' n'existait déjà pas !", result.stdout)

        # Check that the temporary file was not modified
        with open(self.temp_file.name, "r", encoding="UTF-8") as f:
            data = json.load(f)
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]["name"], "item1")
            self.assertEqual(data[1]["name"], "item2")


if __name__ == "__main__":
    unittest.main()
