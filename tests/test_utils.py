import json
import os
import tempfile
import unittest

from app.utils import load_data, save_data, to_lower_snake_case

class TestUtils(unittest.TestCase):
    def setUp(self):
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(b'{"key": "value"}')
        self.temp_file.close()

    def tearDown(self):
        # Clean up the temporary file
        os.remove(self.temp_file.name)

    def test_should_load_data(self):
        data = load_data(self.temp_file.name)
        self.assertEqual(data, {"key": "value"})

    def test_should_save_data(self):
        data = {"key": "new_value"}
        save_data(self.temp_file.name, data)
        with open(self.temp_file.name, 'r', encoding="UTF-8") as f:
            saved_data = json.load(f)
            self.assertEqual(saved_data, data)

    def test_should_lower_snake_case_input(self):
        self.assertEqual(to_lower_snake_case("TestString"), "test_string")
        self.assertEqual(to_lower_snake_case("Test String"), "test_string")
        self.assertEqual(to_lower_snake_case("TestStringWithNumbers123"), "test_string_with_numbers123")
        self.assertEqual(to_lower_snake_case("TestStringWithSpaces  "), "test_string_with_spaces")
        self.assertEqual(to_lower_snake_case("  TestStringWithSpaces"), "test_string_with_spaces")

if __name__ == '__main__':
    unittest.main()
