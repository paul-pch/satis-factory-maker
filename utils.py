import json

def load_data(file_path):
    with open(file_path, 'r', encoding="UTF-8") as file:
        return json.load(file)

def save_data(file_path, recipes):
    with open(file_path, 'w', encoding="UTF-8") as file:
        json.dump(recipes, file, indent=4)
