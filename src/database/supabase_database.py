from config.supabase_config import SupabaseConfig
from errors.supabase_error import *


class SupabaseDatabaseClient:
    def __init__(self):
        self.config = SupabaseConfig.get_config()
        self.credentials = None
        self.app = None

    def __get_app_creds(self):
        if self.credentials is None:
            self.credentials = None

    def initialize_app(self):
        try:
            if self.firebase is None:
                pass
        except ValueError as e:
            raise SupabaseAppInitializationException(
                f"Failed to initialize the app: {e}"
            )
