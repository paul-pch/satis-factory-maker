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
        recipes_data = [
            {
                "name": "test_recipe",
                "machine": "test_machine",
                "input": {"item1": 1.0},
                "output": {"item2": 2.0},
            }
        ]
        with open(self.temp_file.name, "w", encoding="utf-8") as f:
            json.dump(recipes_data, f)

        # Create a temporary file for the items.json file
        self.items_file = tempfile.NamedTemporaryFile(delete=False)
        items_data = [{"name": "item1"}, {"name": "item2"}, {"name": "item3"}]
        with open(self.items_file.name, "w", encoding="utf-8") as f:
            json.dump(items_data, f)

        # Patch the load_data and save_data functions to use the temporary files
        self.load_data_patch = patch(
            "app.recipe.load_data",
            side_effect=lambda file_path: load_data(
                self.temp_file.name
                if file_path == "recipes.json"
                else self.items_file.name
            ),
        )
        self.save_data_patch = patch(
            "app.recipe.save_data",
            side_effect=lambda file_path, data: save_data(self.temp_file.name, data),
        )
        self.load_data_patch.start()
        self.save_data_patch.start()

    def tearDown(self):
        # Clean up the temporary files
        os.remove(self.temp_file.name)
        os.remove(self.items_file.name)
        self.load_data_patch.stop()
        self.save_data_patch.stop()

    def test_should_edit_recipe(self):
        runner = CliRunner()

        # Test case 1: Edit a recipe with a new machine and modified input and output items
        result = runner.invoke(
            app,
            ["edit", "--name", "test_recipe", "--machine", "new_machine"],
            input="item1\n2.0\ndone\nitem2\n3.0\ndone\n",
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Recette modifiée avec succès!", result.stdout)
        with open(self.temp_file.name, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["name"], "test_recipe")
            self.assertEqual(data[0]["machine"], "new_machine")
            self.assertEqual(data[0]["input"], {"item1": 2.0})
            self.assertEqual(data[0]["output"], {"item2": 3.0})

    def test_should_not_edit_recipe_when_invalid_name(self):
        runner = CliRunner()

        # Test case: Edit a recipe with an invalid name
        result = runner.invoke(
            app,
            ["edit", "--name", "invalid_recipe", "--machine", "new_machine"],
            input="item1\n2.0\ndone\nitem2\n3.0\ndone\n",
        )
        self.assertEqual(result.exit_code, 1)
        self.assertNotIn("Recette modifiée avec succès!", result.stdout)
        self.assertIn("La recette 'invalid_recipe' n'existe pas.", result.stdout)
        with open(self.temp_file.name, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["name"], "test_recipe")
            self.assertEqual(data[0]["machine"], "test_machine")
            self.assertEqual(data[0]["input"], {"item1": 1.0})
            self.assertEqual(data[0]["output"], {"item2": 2.0})

    def test_should_edit_recipe_when_valid_input_item_finaly_given(self):
        runner = CliRunner()

        # Test case: Edit a recipe with an invalid input item
        result = runner.invoke(
            app,
            ["edit", "--name", "test_recipe", "--machine", "new_machine"],
            input="item4\nitem1\n5.0\ndone\nitem2\n3.0\ndone\n",
        )

        self.assertEqual(result.exit_code, 0)
        self.assertIn("L'item 'item4' n'existe pas. Veuillez réessayer.", result.stdout)
        self.assertIn("Recette modifiée avec succès!", result.stdout)
        with open(self.temp_file.name, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["name"], "test_recipe")
            self.assertEqual(data[0]["machine"], "new_machine")
            self.assertEqual(data[0]["input"], {"item1": 5.0})
            self.assertEqual(data[0]["output"], {"item2": 3.0})
