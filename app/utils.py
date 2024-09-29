import json
import os
import re

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


def load_data(file_name):
    file_path = os.path.join(DATA_DIR, file_name)
    with open(file_path, 'r', encoding="UTF-8") as file:
        return json.load(file)

def save_data(file_name, data):
    file_path = os.path.join(DATA_DIR, file_name)
    with open(file_path, 'w', encoding="UTF-8") as file:
        json.dump(data, file, indent=4)

def to_lower_snake_case(name):
    name = name.strip()
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)
    s3 = re.sub(' +', ' ', s2)
    return s3.lower().replace(' ', '_')
