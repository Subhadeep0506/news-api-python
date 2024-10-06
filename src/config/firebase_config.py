import json

from .base_config import Config


class FirebaseConfig(Config):
    with open("secrets/firebase-config.json") as f:
        config = json.load(f)
