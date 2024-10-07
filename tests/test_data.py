import json
import pytest
import requests_mock
from app import data


@pytest.fixture
def mock_data():
    return {"test_key": "test_value"}


def test_fetch(mock_data):
    url = "http://test.com"
    with requests_mock.Mocker() as m:
        m.get(url, json=mock_data)
        data.fetch(url)

    with open("data/data.json", "r", encoding="utf-8") as f:
        saved_data = json.load(f)

    assert saved_data == mock_data
