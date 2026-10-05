import json

import pytest
import typer

from app.utils import load_data


def test_should_load_json_file(tmp_path):
    file = tmp_path / "data.json"
    file.write_text(json.dumps({"items": []}))
    assert load_data(str(file)) == {"items": []}


def test_should_exit_when_file_is_missing(tmp_path):
    with pytest.raises(typer.Exit):
        load_data(str(tmp_path / "missing.json"))


def test_should_exit_when_file_is_not_json(tmp_path):
    file = tmp_path / "data.json"
    file.write_text("not json")
    with pytest.raises(typer.Exit):
        load_data(str(file))
