import json

from .base_config import Config


class SupabaseConfig(Config):
    config = None
    with open("secrets/supabase-config.json") as f:
        config = json.load(f)
