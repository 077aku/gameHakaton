import json
import os

FILE_PATH = "player_data.json"

DEFAULT_DATA = {
    "xp": 0,
    "level": 1,
    "upgrades": {
        "extra_life": 0,
        "shield_chance": 0,
        "multi_shot_chance": 0
    }
}

def load_progress():
    if not os.path.exists(FILE_PATH):
        save_progress(DEFAULT_DATA)
    with open(FILE_PATH, "r") as file:
        return json.load(file)

def save_progress(data):
    with open(FILE_PATH, "w") as file:
        json.dump(data, file, indent=4)

def add_xp(score):
    data = load_progress()
    data["xp"] += score

    while data["xp"] >= data["level"] * 100:
        data["xp"] -= data["level"] * 100
        data["level"] += 1

    save_progress(data)

