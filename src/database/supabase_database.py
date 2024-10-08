from config.firebase_config import FirebaseConfig
from errors.firebase_error import *


class SupabaseDatabaseClient:
    def __init__(self):
        self.config = FirebaseConfig.get_config()
        self.credentials = None
        self.firebase = None

    def __get_app_creds(self):
        if self.credentials is None:
            self.credentials = Certificate("secrets/firebase-credentials.json")

    def initialize_app(self):
        try:
            if self.firebase is None:
                self.__get_app_creds()
                self.firebase = initialize_app(
                    credential=self.credentials, options=self.config
                )
        except ValueError as e:
            raise FirebaseAppInitializationException(
                f"Failed to initialize the app: {e}"
            )
