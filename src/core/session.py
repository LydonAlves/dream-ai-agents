import os
import json

# This block handles session management.

# Sets a directory where user session data will be stored as .json files.
# THIS MUST BE CHANGED TO A DATABASE
SESSION_PATH = "./session_data/"


# finds or creates a session folder
def get_session_context(user_id: str, dream_id: str) -> dict:
    os.makedirs(SESSION_PATH, exist_ok=True)
    filepath = os.path.join(SESSION_PATH, f"{user_id}_{dream_id}.json")
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {}


# Saves session context dictionary back to their session file
def save_session_context(user_id: str, dream_id: str, context: dict):
    os.makedirs(SESSION_PATH, exist_ok=True)
    filepath = os.path.join(SESSION_PATH, f"{user_id}_{dream_id}.json")
    with open(filepath, "w") as f:
        json.dump(context, f)
