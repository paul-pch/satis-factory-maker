import json
import os
import tempfile
import unittest
from unittest.mock import patch

from typer.testing import CliRunner

from app.item import app
from app.utils import load_data, save_data


class TestItemCreate(unittest.TestCase):
    def setUp(self):
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(b"[]")
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

    # Create section tests

    def test_should_create_item(self):
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "create",
                "--name",
                "test_item",
                "--description",
                "This is a test item",
                "--tier",
                "5",
            ],
        )

        # Check that the command was successful
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Item 'test_item' ajouté avec succès!", result.stdout)

        # Check that the item was added to the temporary file
        with open(self.temp_file.name, "r", encoding="UTF-8") as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["name"], "test_item")
            self.assertEqual(data[0]["description"], "This is a test item")
            self.assertEqual(data[0]["tier"], 5)

    def test_should_create_item_with_lowersnakecase_name(self):
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "create",
                "--name",
                "un nom ditem avec espaces45",
                "--description",
                "This is a test item",
                "--tier",
                "5",
            ],
        )

        # Check that the command was successful
        self.assertEqual(result.exit_code, 0)
        self.assertIn(
            "Item 'un_nom_ditem_avec_espaces45' ajouté avec succès!", result.stdout
        )

        # Check that the item was added to the temporary file
        with open(self.temp_file.name, "r", encoding="UTF-8") as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["name"], "un_nom_ditem_avec_espaces45")
            self.assertEqual(data[0]["description"], "This is a test item")
            self.assertEqual(data[0]["tier"], 5)

    def test_should_fail_creating_item_already_existing(self):
        # Add an item to the temporary file
        with open(self.temp_file.name, "w", encoding="UTF-8") as f:
            json.dump(
                [
                    {
                        "name": "test_item",
                        "description": "This is a test item",
                        "tier": 5,
                    }
                ],
                f,
            )

        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "create",
                "--name",
                "test_item",
                "--description",
                "This is a test item",
                "--tier",
                "5",
            ],
        )

        # Check that the command was successful
        self.assertEqual(result.exit_code, 0)
        self.assertIn("L'item 'test_item' existe déjà.", result.stdout)

        # Check that the temporary file was not modified
        with open(self.temp_file.name, "r", encoding="UTF-8") as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["name"], "test_item")
            self.assertEqual(data[0]["description"], "This is a test item")
            self.assertEqual(data[0]["tier"], 5)
