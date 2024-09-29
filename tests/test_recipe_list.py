import os
import tempfile
import unittest
from unittest.mock import patch

from typer.testing import CliRunner

from app.recipe import app
from app.utils import load_data


class TestRecipeList(unittest.TestCase):
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
        self.load_data_patch.start()

    def tearDown(self):
        # Clean up the temporary file
        os.remove(self.temp_file.name)
        self.load_data_patch.stop()

    def test_list_recipes(self):
        runner = CliRunner()
        result = runner.invoke(app, ["list"])

        # Check that the command was successful
        self.assertEqual(result.exit_code, 0)

        # Check that the output contains the expected recipe
        self.assertIn("test_machine", result.stdout)
        self.assertIn("test_recipe", result.stdout)
        self.assertIn("item1: 1.0/min", result.stdout)
        self.assertIn("item2: 2.0/min", result.stdout)


if __name__ == "__main__":
    unittest.main()
