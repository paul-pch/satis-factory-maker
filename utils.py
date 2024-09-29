import json
import re

def load_data(file_path):
    with open(file_path, 'r', encoding="UTF-8") as file:
        return json.load(file)

def save_data(file_path, recipes):
    with open(file_path, 'w', encoding="UTF-8") as file:
        json.dump(recipes, file, indent=4)

def to_lower_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
