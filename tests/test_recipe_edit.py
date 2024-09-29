import json
import os
import tempfile
import unittest
from unittest.mock import patch

from typer.testing import CliRunner

from app.recipe import app
from app.utils import load_data, save_data


class TestRecipeEdit(unittest.TestCase):
    def setUp(self):
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(
            b'[{"name": "test_recipe", "machine": "test_machine", "input": {"item1": 1.0}, "output": {"item2": 2.0}}]'
        )
        self.temp_file.close()

        # Patch the load_data and save_data functions to use the temporary file
        self.load_data_patch = patch(
            "app.recipe.load_data", side_effect=lambda _: load_data(self.temp_file.name)
        )
        self.save_data_patch = patch(
            "app.recipe.save_data",
            side_effect=lambda file_path, data: save_data(self.temp_file.name, data),
        )
        self.load_data_patch.start()
        self.save_data_patch.start()

    def tearDown(self):
        # Clean up the temporary file
        os.remove(self.temp_file.name)
        self.load_data_patch.stop()
        self.save_data_patch.stop()

    def test_should_edit_recipe(self):
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "edit",
                "--name",
                "test_recipe",
                "--new-name",
                "new_recipe",
                "--new-machine",
                "new_machine",
                "--new-input",
                "item3:3.0",
                "--new-output",
                "item4:4.0",
            ],
        )

        # Check that the command was successful
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Recette modifiée avec succès!", result.stdout)

        # Check that the recipe was edited in the temporary file
        with open(self.temp_file.name, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["name"], "new_recipe")
            self.assertEqual(data[0]["machine"], "new_machine")
            self.assertEqual(data[0]["input"], {"item3": 3.0})
            self.assertEqual(data[0]["output"], {"item4": 4.0})

    def test_should_not_edit_nonexistent_recipe(self):
        runner = CliRunner()
        result = runner.invoke(app, ["edit", "--name", "nonexistent_recipe"])

        # Check that the command was successful
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Recette 'nonexistent_recipe' non trouvée.", result.stdout)

        # Check that the temporary file was not modified
        with open(self.temp_file.name, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["name"], "test_recipe")
            self.assertEqual(data[0]["machine"], "test_machine")
            self.assertEqual(data[0]["input"], {"item1": 1.0})
            self.assertEqual(data[0]["output"], {"item2": 2.0})


if __name__ == "__main__":
    unittest.main()
