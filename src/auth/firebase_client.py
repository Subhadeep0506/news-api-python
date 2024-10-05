import pyrebase

from config.firebase_config import config


class FirebaseClient:
    def __init__(self):
        self.config = config

    def initialize_app(self):
        firebase = pyrebase.initialize_app(self.config)
        return firebase
