import json
import os

DATA_PATH = "player_data.json"

default_data = {
    "lives": 3,
    "damage": 1,
    "speed": 5,
    "level": 1,
    "exp": 0
}

def load_data():
    if not os.path.exists(DATA_PATH):
        save_data(default_data)
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)

def upgrade_stat(stat):
    data = load_data()
    if stat == "lives":
        data["lives"] += 1
    elif stat == "damage":
        data["damage"] += 1
    elif stat == "speed":
        data["speed"] += 1
    save_data(data)
