import json
import os
import config as cfg

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE = os.path.join(BASE_DIR, "save.json")

def load_progress():
    default_data = {"unlocked_level": 1, "plants_count": 1}
    if not os.path.exists(SAVE_FILE):
        print("не знайшло шлях")
        return default_data
    try:
        with open(SAVE_FILE, 'r') as f:
            return json.load(f)
    except:
        return default_data

def save_progress(lvl_completed):
    data = load_progress()
    just_unlocked_something = False

    if lvl_completed + 1 > data["unlocked_level"]:
        data["unlocked_level"] = lvl_completed + 1
        just_unlocked_something = True 

    new_plants = 1
    if lvl_completed < 4: new_plants = lvl_completed + 1
    elif lvl_completed == 4: new_plants = 4 
    else: new_plants = lvl_completed 

    if new_plants > data.get("plants_count", 1):
        data["plants_count"] = min(new_plants, 6)
        
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f)
    
    return just_unlocked_something