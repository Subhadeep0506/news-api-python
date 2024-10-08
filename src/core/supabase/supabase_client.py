from supabase import create_client
from ...config.supabase_config import SupabaseConfig


class SupabaseClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.__init__(cls._instance)
        return cls._instance.app

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.initialized = True
            self.app = None
            self.url = SupabaseConfig.get_config().get("uri")
            self.key = SupabaseConfig.get_config().get("key")
            self.__init_app()

    def __init_app(self):
        self.app = create_client(self.url, self.key)
