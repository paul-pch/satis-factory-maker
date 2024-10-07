import json
import os
import tempfile

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
            ]
        }
        self.temp_dir = tempfile.mkdtemp()
        with open(os.path.join(self.temp_dir, "data.json"), "w", encoding="utf-8") as f:
            json.dump(self.fake_data, f)

    def test_item_search(self):
        result = self.runner.invoke(
            app, ["item", "--query", "Test Item 1"], env={"DATA_DIR": self.temp_dir}
        )

        print(result.output)

        assert result.exit_code == 0
        assert "Test Item 1" in result.output
        assert "test_item_1" in result.output
        assert "1" in result.output
        assert "10" in result.output

        result = self.runner.invoke(app, ["item", "--query", "Non-existent Item"])
        assert result.exit_code == 0
        assert "No items found matching 'Non-existent Item'" in result.output
