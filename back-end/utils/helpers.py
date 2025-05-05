import json
import os

def save_user_to_file(user):
    path = f"data/{user.id}.json"
    with open(path, 'w') as f:
        json.dump(user.__dict__, f, default=str)

def load_user_from_file(user_id):
    path = f"data/{user_id}.json"
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
