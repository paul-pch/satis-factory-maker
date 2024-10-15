import json
import os
import tempfile
import unittest
from app.utils import load_data


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.test_data = {"key": "value"}
        with open(self.temp_file.name, "w") as f:
            json.dump(self.test_data, f)

    def tearDown(self):
        os.remove(self.temp_file.name)

    def test_load_data(self):
        data = load_data(self.temp_file.name)
        self.assertEqual(data, self.test_data)

    def test_load_data_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            load_data("non_existent_file.json")
