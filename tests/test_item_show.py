import os
import tempfile
import unittest
from unittest.mock import patch

from typer.testing import CliRunner

from app.item import app
from app.utils import load_data


class TestItemShow(unittest.TestCase):
    def setUp(self):
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(
            b'[{"name": "item1", "description": "description1", "tier": 1}, {"name": "item2", "description": "description2"}]'
        )
        self.temp_file.close()

        # Patch the load_data function to use the temporary file
        self.load_data_patch = patch(
            "app.item.load_data", side_effect=lambda _: load_data(self.temp_file.name)
        )
        self.load_data_patch.start()

    def tearDown(self):
        # Clean up the temporary file
        os.remove(self.temp_file.name)
        self.load_data_patch.stop()

    def test_should_show_all_items(self):
        runner = CliRunner()
        result = runner.invoke(app, ["show"])

        # Check that the command was successful
        self.assertEqual(result.exit_code, 0)

        # Check that the output contains the expected items
        self.assertIn("item1", result.stdout)
        self.assertIn("description1", result.stdout)
        self.assertIn("1", result.stdout)
        self.assertIn("item2", result.stdout)
        self.assertIn("description2", result.stdout)
        self.assertIn("Non spécifié", result.stdout)


if __name__ == "__main__":
    unittest.main()
